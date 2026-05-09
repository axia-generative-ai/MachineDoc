from sqlalchemy import Column, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class ErrorCode(Base):
    __tablename__ = "error_code"

    error_code_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    
    # 외래키: saved_manual 테이블의 manual_id 참조
    manual_id = Column(BigInteger, ForeignKey("saved_manual.manual_id"), nullable=False)
    
    # 에러 코드 이름 (예: E-102, ERR_MOTOR_01 등)
    code_name = Column(String(255), nullable=False)

    # 관계 설정: 이 에러 코드가 어떤 매뉴얼에 포함되어 있는지 바로 접근 가능
    manual = relationship("SavedManual", back_populates="error_codes")