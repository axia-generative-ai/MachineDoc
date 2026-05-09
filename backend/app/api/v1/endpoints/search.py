from fastapi import APIRouter, Depends, Query, status
from app.service.search_service import search_service
from app.schemas.search import AIQueryRequest, AIQueryResponse
from app.models.user import User
from sqlalchemy.orm import Session
from app.api import deps

router = APIRouter()

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

@router.post(
    "/diagnosis",
    response_model=AIQueryResponse,
    status_code=status.HTTP_200_OK,
    summary="AI에게 이상 징후 문의",
    responses={
        200: {
            "description": "분석 성공",
            "content": {
                "application/json": {
                    "example": {
                        "answer": "해당 설비의 온도 수치(95.5)는 임계치를 초과했습니다. 냉각 시스템 점검이 필요합니다.",
                        "status": "success"
                    }
                }
            }
        },
        503: {
            "description": "AI 서버 통신 오류 (이력은 저장됨)",
            "content": {
                "application/json": {
                    "example": {"detail": "AI 분석 요청 처리 중 오류가 발생하여 이력을 기록하고 중단했습니다."}
                }
            }
        },
        401: {"description": "인증되지 않은 사용자"}
    }
)
async def diagnosis(
    request_data: AIQueryRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    통합 알림 상세 페이지에서 발생한 이상 징후에 대해 AI 서버의 분석을 요청합니다.
    
    ### 주요 프로세스:
    1. **데이터 가공**: 전달받은 설비 코드, 데이터 타입, 수치를 조합하여 AI 분석용 쿼리를 생성합니다.
    2. **AI 서버 통신**: 생성된 쿼리를 AI 모델 서버로 전송하여 진단 결과를 받아옵니다.
    3. **이력 자동 저장**: AI 서버의 응답 성공 여부와 관계없이, 모든 요청 내용은 **search_history** 테이블에 기록됩니다.
    4. **실패 대응**: AI 서버 통신 실패 시 **AI_ERROR** 상태로 이력을 남긴 후 사용자에게 에러를 반환합니다.
    
    - **인증**: 로그인이 필요한 서비스이며, 요청한 사용자의 ID가 검색 이력의 소유자로 저장됩니다.
    - 비즈니스 로직은 search_service.process_ai_query에서 처리됩니다.
    """
    return await search_service.process_ai_query(db, request_data, current_user.user_id)

