from sqlalchemy import Column, BigInteger, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class SearchHistory(Base):
    __tablename__ = "search_history"

    history_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    
    # 1:N 관계 - 어떤 사용자가 검색했는가
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    
    # 1:1 관계 - 어떤 로그를 보고 검색을 유도했는가 (Nullable)
    log_id = Column(BigInteger, ForeignKey("log.log_id"), nullable=True, unique=True)
    
    query = Column(String(255), nullable=False) # 검색어
    result_content = Column(Text, nullable=False) # 검색 결과 (JSON 형태 등으로 저장)
    status = Column(String(50), nullable=False) # 상태 (단순 검색, 조치 연결 등)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 관계 설정
    user = relationship("User", back_populates="search_histories")
    log = relationship("EquipmentLog", back_populates="search_history")
    # 조치 이력과의 1:1 관계
    action_log = relationship("ActionLog", back_populates="search_history", uselist=False)