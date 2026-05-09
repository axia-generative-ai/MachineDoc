from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.service.search_service import search_service
from app.service.action_log_service import action_log_service
from app.models.user import User
from app.schemas.search_history import SearchHistoryRead
from app.schemas.action_log import ActionLogCreate, ActionLogRead, ActionLogWithHistory
from sqlalchemy.orm import Session
from app.api import deps

router = APIRouter()


@router.get(
    "/history",
    summary="내 검색 이력 조회",
    response_model=List[SearchHistoryRead],
)
def list_my_search_history(
    limit: int = Query(50, le=200, description="최근 N건"),
    status: Optional[str] = Query(None, description="필터: COMPLETED / INVALID_CODE / AI_ERROR"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    로그인한 사용자 본인의 검색 이력을 최신순으로 반환합니다.
    - status 미지정 시 전체 반환.
    - 다른 사용자의 이력은 노출되지 않습니다.
    """
    return search_service.list_user_history(db, user_id=current_user.user_id, limit=limit, status=status)


@router.get(
    "/actions",
    summary="내 조치 이력 조회",
    response_model=List[ActionLogWithHistory],
)
def list_my_action_history(
    limit: int = Query(50, le=200),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    로그인한 사용자 본인이 저장한 조치 이력을 최신순으로 반환합니다.
    - 각 조치에는 원본 검색 query / status / 검색 일시가 함께 포함됩니다.
    """
    return action_log_service.list_for_user(db, user_id=current_user.user_id, limit=limit)


@router.post(
    "/history/{history_id}/action",
    summary="조치 결과 등록",
    response_model=ActionLogRead,
)
def upsert_action_for_history(
    history_id: int,
    obj_in: ActionLogCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    특정 검색 이력에 대해 작업자가 수행한 조치 결과를 저장합니다.
    - **history_id**: 조치 대상 검색 이력 ID
    - **action_sta**: 조치 상태 (`완료` / `부분 완료` / `추가 점검 필요` / `조치 불가`)
    - **comment**: 자유 메모 (선택)
    - **duration**: 소요 시간 (분, 선택)
    - 동일 history_id에 대한 조치가 이미 있다면 덮어씁니다 (search_history 1:1 unique).
    - 본인 검색 이력이 아닐 경우 403.
    """
    return action_log_service.create_or_update(
        db,
        user_id=current_user.user_id,
        history_id=history_id,
        obj_in=obj_in,
    )


@router.get("/code", summary="오류 코드 기반 AI 분석 및 이력 저장")
async def search_error_code(
    error_code: str = Query(..., description="검색할 오류 코드 (예: E0001)", examples="E0001"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    장비에서 발생한 오류 코드를 입력하면 AI 서버를 통해 분석 결과를 반환하고, 동시에 사용자의 검색 이력을 시스템에 기록합니다.
    
    * **검색 성공**: AI 분석 결과 반환 및 'COMPLETED' 상태로 저장
    * **잘못된 코드**: 404 에러 반환 및 'INVALID_CODE' 상태로 이력 저장
    * **AI 서버 오류**: 503 에러 반환 및 'AI_ERROR' 상태로 이력 저장

    - **error_code**: 현장에서 발생한 에러 코드 문자열
    - **auth**: 로그인한 사용자 토큰 필요
    """
    result = await search_service.get_ai_diagnosis(db, error_code, current_user.user_id)
    return result

