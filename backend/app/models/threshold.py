from sqlalchemy import Column, BigInteger, ForeignKey, Float, Enum, String
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.log import DataType  # 이전에 정의한 DataType Enum 사용

class EquipmentThreshold(Base):
    __tablename__ = "equipment_threshold"

    threshold_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    
    # 어느 설비의 임계값인지 참조
    equipment_id = Column(BigInteger, ForeignKey("equipment.equipment_id"), nullable=False)
    
    # 어떤 데이터 타입(온도/진동)에 대한 설정인지
    data_type = Column(Enum(DataType), nullable=False)
    
    # 수치 기준
    warning_threshold = Column(Float, nullable=False, comment="위험 상태 기준값")
    error_threshold = Column(Float, nullable=False, comment="오류 상태 기준값")

    # 관계 설정
    equipment = relationship("Equipment", back_populates="thresholds")