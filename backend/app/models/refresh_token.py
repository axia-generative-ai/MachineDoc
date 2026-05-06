from sqlalchemy import Column, String, BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    # token_id: BIGINT, PK, AI
    token_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)

    # user_id: BIGINT, NN, FK (User 테이블의 user_id 참조)
    # 1:1 관계를 위해 unique=True 설정을 추가하는 것이 좋습니다.
    user_id = Column(
        BigInteger, 
        ForeignKey("users.user_id", ondelete="CASCADE"), 
        nullable=False, 
        unique=True
    )

    # token: VARCHAR, NN, UNIQUE
    token = Column(String(512), nullable=False, unique=True, index=True)

    # expires_at: TIMESTAMP, NN
    expires_at = Column(DateTime(timezone=True), nullable=False)

    # created_at: TIMESTAMP, NN
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # --- 관계 설정 (선택 사항이지만 권장) ---
    # User 모델과의 관계를 설정하여 편리하게 참조할 수 있습니다. (Spring의 @OneToOne과 유사)
    user = relationship("User", backref="refresh_token", uselist=False)