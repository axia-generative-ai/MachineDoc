import enum
from sqlalchemy import Column, BigInteger, Float, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

# 데이터 타입 정의
class DataType(str, enum.Enum):
    VIBRATION = "VIBRATION"
    TEMPERATURE = "TEMPERATURE"

# 로그 상태 정의
class LogStatus(str, enum.Enum):
    NORMAL = "정상"
    WARNING = "위험"
    ERROR = "오류"

class EquipmentLog(Base):
    __tablename__ = "log"

    log_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    
    # 외래키: equipment 테이블의 equipment_id 참조
    equipment_id = Column(BigInteger, ForeignKey("equipment.equipment_id", ondelete="CASCADE"), nullable=False)
    
    data_type = Column(Enum(DataType), nullable=False)
    value = Column(Float, nullable=False)
    
    # 상태 (정상, 위험, 오류)
    status = Column(Enum(LogStatus), nullable=False, default=LogStatus.NORMAL)
    
    # 발생 시각
    occurred_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # 관계 설정: 로그에서 설비 정보에 바로 접근 가능
    equipment = relationship("Equipment", back_populates="logs")
    notification = relationship("Notification", back_populates="log", uselist=False, cascade="all, delete-orphan")
    search_history = relationship("SearchHistory", back_populates="log", uselist=False, cascade="all, delete-orphan")