import enum
from sqlalchemy import Column, BigInteger, String, Text, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

# 읽음 및 처리 상태 정의
class ReadStatus(str, enum.Enum):
    UNREAD = "미확인"
    CHECKED = "확인"
    COMPLETED = "완료"

# 알림 중요도 정의
class NotificationLevel(str, enum.Enum):
    URGENT = "긴급"
    WARNING = "경고"
    CAUTION = "주의"

class Notification(Base):
    __tablename__ = "notification"

    notification_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    
    # 외래키: log 테이블의 log_id 참조 (1:1 관계)
    log_id = Column(BigInteger, ForeignKey("log.log_id", ondelete="CASCADE"), nullable=False, unique=True)
    
    message = Column(Text, nullable=False) # 알림 내용
    
    # 상태 (미확인, 확인, 완료)
    is_read = Column(Enum(ReadStatus), nullable=False, default=ReadStatus.UNREAD)
    
    # 중요도 (긴급, 경고, 주의)
    level = Column(Enum(NotificationLevel), nullable=False)
    
    # 발생 시각 (로그 발생 시각과 맞춤)
    occurred_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # 알림 생성 시점에 (equipment, data_type) + anomaly_rules.json 기반으로 결정된
    # 추천 오류코드. 같은 알림을 새로고침해도 동일한 코드가 노출되도록 박제 저장.
    suggested_error_code = Column(String(50), nullable=True)

    # 관계 설정: 알림에서 해당 로그 정보에 바로 접근 가능
    log = relationship("EquipmentLog", back_populates="notification")