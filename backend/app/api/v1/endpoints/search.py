from fastapi import APIRouter, Depends, Query
from app.service.search_service import search_service
from app.models.user import User
from sqlalchemy.orm import Session
from app.api import deps

router = APIRouter()

@router.get("/code", summary="오류 코드 기반 AI 분석 및 이력 저장")
async def search_error_code(
    error_code: str = Query(..., description="검색할 오류 코드 (예: E0001)", example="E0001"),
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