import re
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
import json
from app.core.ai_client import call_ai_server
from app.crud.crud_error_code import error_code_repository
from app.crud.crud_search_history import search_history_repository
from app.models.saved_manual import SavedManual

# ai-service 응답에 들어오는 인용 표기 두 형식을 모두 잡는다:
#   "(출처: file.pdf p12)"
#   "(출처: file.pdf, 페이지 12)" / "(출처: file.pdf, p.12)"
_CITATION_RE = re.compile(
    r"\(출처:\s*([^),\s]+\.pdf)\s*,?\s*(?:페이지[:\s]*|p\.?\s*)(\d+)\)",
    re.IGNORECASE,
)


def _extract_citations(db: Session, *texts: str) -> list[dict]:
    """analysis/solution 텍스트에서 (filename, page) 추출 → manual_id 매핑.

    - 동일 (filename, page) 쌍은 한 번만 반환 (순서 유지)
    - saved_manual.file_url에 매칭되는 manual_id를 채워서 FE가 PDF 직접 오픈 가능
    """
    seen: set[tuple[str, str]] = set()
    pairs: list[tuple[str, str]] = []
    for text in texts:
        if not text:
            continue
        for match in _CITATION_RE.finditer(text):
            key = (match.group(1), match.group(2))
            if key in seen:
                continue
            seen.add(key)
            pairs.append(key)

    if not pairs:
        return []

    # file_url 일괄 조회 → dict
    filenames = {fn for fn, _ in pairs}
    rows = (
        db.query(SavedManual.manual_id, SavedManual.file_url)
        .filter(SavedManual.file_url.in_(filenames))
        .all()
    )
    fname_to_id = {row.file_url: row.manual_id for row in rows}

    return [
        {
            "filename": fn,
            "page": int(page),
            "manual_id": fname_to_id.get(fn),
        }
        for fn, page in pairs
    ]


class SearchService:
    def list_user_history(self, db: Session, *, user_id: int, limit: int = 50, status: Optional[str] = None):
        return search_history_repository.list_by_user(db, user_id=user_id, limit=limit, status=status)

    async def get_ai_diagnosis(self, db: Session, error_code: str, user_id: int):
        # 1. 초기 상태 설정
        ai_result = None
        search_status = "PENDING"
        raise_exception = False
        history_id = None

        # 2. error_code 검증 로직
        db_error = error_code_repository.get_error_code_by_name(db, error_code.upper())
        try:
            if not db_error:
                search_status = "INVALID_CODE"
                raise ValueError("Unregistered error code")

            # 3. AI 서버 호출
            ai_result = await call_ai_server({"error_code": error_code})
            search_status = "COMPLETED"
        except Exception as e:
            if search_status == "PENDING":
                search_status = "AI_ERROR"
            error_detail = str(e)
            ai_result = {"error": error_detail}
            raise_exception = True

        # 4. 검색 이력 저장 (성공/실패 모두) → history_id 확보
        try:
            saved = search_history_repository.create_search_history(
                db,
                user_id=user_id,
                query=error_code,
                result=json.dumps(ai_result),
                status=search_status,
            )
            history_id = saved.history_id if saved else None
        except Exception:
            history_id = None

        # 5. 실패한 경우 에러 던지기
        if raise_exception:
            if search_status == "INVALID_CODE":
                raise HTTPException(status_code=404, detail="등록되지 않은 코드입니다.")
            raise HTTPException(status_code=503, detail="AI 분석 중 오류가 발생했습니다.")

        # 6. 성공 응답 — 기존 ai_result + history_id + citations 함께 반환
        if isinstance(ai_result, dict):
            citations = _extract_citations(
                db,
                str(ai_result.get("analysis") or ""),
                str(ai_result.get("solution") or ""),
            )
            return {**ai_result, "history_id": history_id, "citations": citations}
        return {"result": ai_result, "history_id": history_id, "citations": []}

# 싱글톤으로 사용하기 위해 인스턴스 생성
search_service = SearchService()