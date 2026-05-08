from sqlalchemy.orm import Session
from app.models.log import EquipmentLog
from app.schemas.log import EquipmentLogCreate

class CRUDLog:
    def create(self, db: Session, *, obj_in: EquipmentLogCreate) -> EquipmentLog:
        # 1. 스키마 데이터를 딕셔너리로 변환 (여기서 model_dump 활용!)
        # exclude_unset=True를 쓰면 기본값이 있는 필드 중 입력되지 않은 것을 제외할 수 있습니다.
        obj_in_data = obj_in.model_dump()
        
        # 2. DB 모델 객체 생성 (언패킹 활용)
        db_obj = EquipmentLog(**obj_in_data)
        
        # 3. DB에 저장 및 반영
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj) # 저장된 후 log_id 등이 채워진 객체를 새로고침
        
        return db_obj

log_repository = CRUDLog()