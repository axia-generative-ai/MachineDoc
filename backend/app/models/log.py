import enum
from sqlalchemy import Column, BigInteger, Float, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

# 데이터 타입 정의
class DataType(str, enum.Enum):
    VIBRATION = "VIBRATION"
    TEMPERATURE = "TEMPERATURE"

# 로그 상태 정의
# NOTE(F7): WARNING="위험"은 NotificationLevel.WARNING="경고"와 한글이 다르다.
# 의도적: log.status 는 (정상/위험/오류) 3단계, notification.level 은 (긴급/경고/주의) 3단계로
# 서로 다른 도메인 라벨을 사용한다. UI 에서 두 enum 을 같은 화면에 붙여 보여줄 때 혼동
# 가능성이 있어 메뉴얼/리뷰 시 주의. DB enum 변경은 마이그레이션 영향이 커 데모 후 정리 예정.
class LogStatus(str, enum.Enum):
    NORMAL = "정상"
    WARNING = "위험"
    ERROR = "오류"

class EquipmentLog(Base):
    __tablename__ = "log"

    log_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    
    # 외래키: equipment 테이블의 equipment_id 참조
    equipment_id = Column(BigInteger, ForeignKey("equipment.equipment_id"), nullable=False)
    
    data_type = Column(Enum(DataType), nullable=False)
    value = Column(Float, nullable=False)
    
    # 상태 (정상, 위험, 오류)
    status = Column(Enum(LogStatus), nullable=False, default=LogStatus.NORMAL)
    
    # 발생 시각
    occurred_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # 관계 설정: 로그에서 설비 정보에 바로 접근 가능
    equipment = relationship("Equipment", back_populates="logs")
    notification = relationship("Notification", back_populates="log", uselist=False, cascade="all, delete-orphan")
    search_history = relationship("SearchHistory", back_populates="log", uselist=False)