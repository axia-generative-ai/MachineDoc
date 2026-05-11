import enum
from sqlalchemy import Column, BigInteger, Text, Integer, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

# 조치 상태 정의
class ActionStatus(str, enum.Enum):
    COMPLETED = "완료"
    PARTIAL = "부분 완료"
    MORE_CHECK = "추가 점검 필요"
    UNAVAILABLE = "조치 불가"

class ActionLog(Base):
    __tablename__ = "action_log"

    action_log_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    
    # 1:1 관계 - 어떤 검색 기록을 바탕으로 조치했는가
    history_id = Column(BigInteger, ForeignKey("search_history.history_id", ondelete="CASCADE"), nullable=False, unique=True)
    
    action_sta = Column(Enum(ActionStatus), nullable=False) # 조치 상태
    comment = Column(Text, nullable=True) # 조치 코멘트
    duration = Column(Integer, nullable=True) # 완료까지 걸린 시간 (분 단위 등)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 관계 설정
    search_history = relationship("SearchHistory", back_populates="action_log")