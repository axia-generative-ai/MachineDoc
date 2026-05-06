from sqlalchemy import Column, BigInteger, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class SavedManual(Base):
    __tablename__ = "saved_manual"

    manual_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    
    # 외래키 설정: users 테이블의 user_id를 참조 (테이블 이름 확인 필요)
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    
    title = Column(String(255), nullable=False)
    file_url = Column(String(500), nullable=False)
    category = Column(String(100), nullable=False) # 설비명 또는 카테고리
    version = Column(String(50), nullable=False)
    
    # 생성 시간 자동 설정
    saved_at = Column(DateTime(timezone=True), server_default=func.now())

    # 관계 설정: 매뉴얼 객체에서 유저 정보를 바로 가져올 수 있게 함
    creator = relationship("User", back_populates="manuals")

    error_codes = relationship("ErrorCode", back_populates="manual", cascade="all, delete-orphan")