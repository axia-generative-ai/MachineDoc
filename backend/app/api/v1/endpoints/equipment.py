from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.db.session import get_db
from app.models.equipment import Equipment
from app.models.user import User
from app.schemas.equipment import InfoEquipmentResponse

router = APIRouter()


@router.get(
    "",
    response_model=list[InfoEquipmentResponse],
    summary="설비 목록",
    description="등록된 모든 설비 목록을 반환합니다. 가상 로그 생성/대시보드 셀렉트 UI 용도.",
)
def list_equipments(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    return db.query(Equipment).order_by(Equipment.equipment_id).all()
