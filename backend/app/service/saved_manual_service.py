import os
import re
import shutil
import httpx
from uuid import uuid4
from fastapi import HTTPException
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.core.ai_client import call_ai_server, AI_SERVER_URL
from app.crud.crud_saved_manual import manual_repository
from fastapi.responses import FileResponse
from app.core.config import config
from app.schemas.manual import ManualCreate, ManualCreateInternal
from app.crud.crud_error_code import error_code_repository
from typing import List

def _slugify(text: str) -> str:
    """ai-service manual_id/equipment_id 슬러그 생성: 영숫자+_- 만 허용, 소문자."""
    s = re.sub(r"[^A-Za-z0-9가-힣]+", "_", text or "").strip("_").lower()
    return s or "manual"

class ManualService:
    def list_error_code_mappings(self, db):
        """error_code × saved_manual join → ErrorCodeMapping list."""
        from app.models.error_code import ErrorCode
        from app.models.saved_manual import SavedManual
        rows = (
            db.query(
                ErrorCode.error_code_id,
                ErrorCode.code_name,
                SavedManual.manual_id,
                SavedManual.title.label("manual_title"),
                SavedManual.category,
                SavedManual.version,
            )
            .join(SavedManual, SavedManual.manual_id == ErrorCode.manual_id)
            .order_by(ErrorCode.code_name)
            .all()
        )
        return [
            {
                "error_code_id": row.error_code_id,
                "code_name": row.code_name,
                "manual_id": row.manual_id,
                "manual_title": row.manual_title,
                "category": row.category,
                "version": row.version,
            }
            for row in rows
        ]
    
    async def get_equipment_manual(self, db, equipment_code, category):
        # 1. DB 우선 조회
        if category:
            manuals = manual_repository.get_manuals_by_category(db, category=category)
        else:
            manuals = manual_repository.get_all_manuals(db) if hasattr(manual_repository, "get_all_manuals") else []

        if manuals:
            return {"source": "database", "data": manuals}

        # 2. DB가 비면 ai-service /manuals/recommend로 fallback (LLM 미사용, ~1s).
        # ai-service는 manual_id를 slug(text)로 반환 → SearchManual.manual_id(int)에
        # 직접 매핑 못한다. saved_manual title 으로 매칭 시도하고, 매칭 실패 시
        # manual_id=0 으로 합성해 FE는 source 필드로 출처를 구분한다.
        try:
            payload = {
                "equipment_id": equipment_code,
                "category": category,
                "top_k": 5,
            }
            url = f"{AI_SERVER_URL.rstrip('/')}/api/v1/manuals/recommend"
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                ai_payload = resp.json()
        except (httpx.HTTPStatusError, httpx.RequestError):
            # ai-service 에 도달 못해도 빈 결과로 graceful degrade
            return {"source": "ai_recommendation", "data": []}

        results = ai_payload.get("results") or []
        from datetime import datetime
        from app.models.saved_manual import SavedManual

        synthesized = []
        for hit in results:
            slug = hit.get("manual_id") or ""
            pretty_title = hit.get("title") or slug.replace("_", " ")

            # 이름 prefix 매칭으로 saved_manual 후보 찾기 (제일 가까운 1건).
            db_manual = None
            if slug:
                db_manual = (
                    db.query(SavedManual)
                    .filter(SavedManual.title.ilike(f"%{slug.split('_')[0]}%"))
                    .first()
                )

            if db_manual:
                synthesized.append({
                    "manual_id": db_manual.manual_id,
                    "title": db_manual.title,
                    "category": db_manual.category,
                    "version": db_manual.version,
                    "saved_at": db_manual.saved_at,
                })
            else:
                synthesized.append({
                    "manual_id": 0,
                    "title": pretty_title,
                    "category": category or "추천",
                    "version": "AI",
                    "saved_at": datetime.utcnow(),
                })

        return {"source": "ai_recommendation", "data": synthesized}
    
    def list_my_manuals(self, db, user_id: int):
        return manual_repository.get_manuals_by_user(db, user_id=user_id)
    
    def get_manual_file_response(self, db, manual_id):
        # 1. DB에서 매뉴얼 정보 조회
        manual = manual_repository.get_manual_by_id(db, manual_id)
        
        if not manual:
            raise HTTPException(status_code=404, detail="매뉴얼을 찾을 수 없습니다.")
        
        # 2. 실제 파일 경로 확인 (DB에는 파일 시스템 경로가 저장되어 있다고 가정)
        file_path = config.MANUAL_URL + manual.file_url  # 예: "/data/manuals/m101_v1.pdf"
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="실제 매뉴얼 파일이 서버에 존재하지 않습니다.")

        # 3. FileResponse로 반환
        # filename은 다운로드 시 기본 파일명이 됩니다.
        return FileResponse(
            path=file_path, 
            media_type="application/pdf",
            filename=f"{manual.title}_{manual.version}.pdf"
        )
    
    async def upload_manual_process(
        self,
        db: Session,
        manual_in: ManualCreate,
        error_codes: List[str],
        file: UploadFile,
        user_id: int
    ):
        # 1. 파일 저장 경로: config.MANUAL_URL이 가리키는 디렉토리에 저장
        # file_url 컬럼에는 파일명만 저장 (get_manual_file_response가 MANUAL_URL + file_url로 조합)
        upload_dir = config.MANUAL_URL
        os.makedirs(upload_dir, exist_ok=True)
        
        original_filename = file.filename or "manual.pdf"
        file_extension = os.path.splitext(original_filename)[1] or ".pdf"
        safe_filename = f"{uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, safe_filename)

        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"서버에 파일을 저장하는 중 오류가 발생했습니다: {str(e)}")

        # 2. DB INSERT (saved_manual + 사용자가 직접 입력한 error_codes)
        try:
            manual_internal = ManualCreateInternal(
                **manual_in.model_dump(),
                user_id=user_id,
                file_url=safe_filename
            )
            new_manual = manual_repository.create(db, manual_internal)

            if error_codes:
                error_code_repository.create_multiple(
                    db,
                    manual_id=new_manual.manual_id,
                    codes=error_codes
                )

            db.commit()
            db.refresh(new_manual)
        except Exception as e:
            db.rollback()
            
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=500, detail=f"데이터베이스 기록 중 오류가 발생했습니다: {str(e)}")
        
        # 3. ai-service로 PDF forward → 청킹/임베딩/색인 (동기, 600초 timeout)
        # ai-service 응답의 error_codes[]를 backend `error_code` 테이블에 추가 sync
        # (사용자 입력 코드와 중복 시 skip)
        ai_manual_slug = _slugify(f"manual_{new_manual.manual_id}_{manual_in.title}")[:80]
        ai_equipment_slug = _slugify(f"eq_{manual_in.category}")[:80]

        existing_codes = {c for c in (error_codes or [])}
        ai_status = "skipped"
        ai_error_codes: List[str] = []
        ai_elapsed_s = 0.0
        ingest_warning: str | None = None

        try:
            with open(file_path, "rb") as fp:
                files = {"file": (original_filename, fp.read(), "application/pdf")}
            data = {
                "manual_id": ai_manual_slug,
                "equipment_id": ai_equipment_slug,
            }
            ingest_url = f"{AI_SERVER_URL.rstrip('/')}/api/v1/ingest"
            async with httpx.AsyncClient(timeout=600.0) as client:
                resp = await client.post(ingest_url, files=files, data=data)
                resp.raise_for_status()
                ingest_result = resp.json()

            ai_error_codes = ingest_result.get("error_codes") or []
            ai_elapsed_s = float(ingest_result.get("elapsed_s") or 0.0)
            ai_status = "indexed"

            # ai-service가 자동 추출한 코드 중 사용자가 입력하지 않은 것만 추가
            new_codes = [code for code in ai_error_codes if code and code not in existing_codes]
            if new_codes:
                error_code_repository.create_multiple(
                    db,
                    manual_id=new_manual.manual_id,
                    codes=new_codes,
                )
                db.commit()
                db.refresh(new_manual)
        except httpx.HTTPStatusError as e:
            ingest_warning = f"ai-service ingest 응답 오류({e.response.status_code}): {e.response.text[:200]}"
            ai_status = "failed"
        except httpx.RequestError as e:
            ingest_warning = f"ai-service 연결 실패: {e}"
            ai_status = "failed"
        except Exception as e:  # noqa: BLE001
            ingest_warning = f"ingest 처리 중 예외: {e}"
            ai_status = "failed"

        # 4. 응답 (ManualResponse 스키마 호환 + 부가 정보)
        message = "매뉴얼이 성공적으로 업로드되었습니다."
        if ai_status == "indexed":
            message += f" (색인 완료, {ai_elapsed_s:.1f}s, 자동 추출 코드 {len(ai_error_codes)}개)"
        elif ai_status == "failed":
            message += f" (단, AI 색인 실패: {ingest_warning})"
        return {
            "manual_id": new_manual.manual_id,
            "title": new_manual.title,
            "message": message,
        }
    
manual_service = ManualService()