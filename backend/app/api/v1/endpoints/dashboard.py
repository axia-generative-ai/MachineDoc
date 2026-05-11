from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
from app.schemas.dashboard import DashboardSummary
from app.service.dashboard_service import dashboard_service

router = APIRouter()

@router.get(
    "/summary",
    summary="대시보드 통합 요약 정보 조회",
    description="통계 카드, 24시간 이상징후 추이, 최근 미확인 이상징후 리스트를 한 번에 조회합니다.",
    response_model=DashboardSummary,
)
def get_dashboard_summary(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    return dashboard_service.get_summary(db)