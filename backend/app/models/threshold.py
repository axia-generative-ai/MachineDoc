from sqlalchemy import Column, BigInteger, ForeignKey, Float, Enum, String
from sqlalchemy.orm import relationship
# app.db.base 는 모든 모델을 모아 Base.metadata 를 구성하는 aggregator.
# threshold 가 거기서 Base 를 가져오면 base.py → threshold.py → base.py 순환.
# Base 는 session.py 가 단독 소유하므로 직접 가져오면 순환이 끊긴다.
from app.db.session import Base
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