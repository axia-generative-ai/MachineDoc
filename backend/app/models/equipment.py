import enum
from sqlalchemy import Column, BigInteger, String, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

# 1. 위치 타입 정의
class LocationType(str, enum.Enum):
    LINE_A = "line_A"
    LINE_B = "line_B"
    LINE_C = "line_C"

# 2. 설비 상태 정의
class EquipmentStatus(str, enum.Enum):
    RUNNING = "가동 중"
    STOPPED = "정지"
    MAINTENANCE = "점검"
    ERROR = "에러"

# 3. 설비 모델 클래스
class Equipment(Base):
    __tablename__ = "equipment"

    equipment_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    location = Column(Enum(LocationType), nullable=False)
    equipment_code = Column(String(50), nullable=False, unique=True, index=True)
    state = Column(Enum(EquipmentStatus), nullable=False, default=EquipmentStatus.STOPPED)
    
    # 이력 추적을 위한 시간 기록 (추천)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    logs = relationship("EquipmentLog", back_populates="equipment", cascade="all, delete-orphan")