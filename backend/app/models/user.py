import enum
from sqlalchemy import Column, String, BigInteger, Enum, DateTime, func
from sqlalchemy.orm import relationship
from app.db.session import Base

# --- ENUM 클래스 정의 (Spring의 Enum과 동일한 역할) ---

class DepartmentType(str, enum.Enum):
    DEPT_A = "라인A 보전팀"
    DEPT_B = "라인B 보전팀"
    DEPT_C = "라인C 보전팀"
    DEPT_ADMIN = "관리자 부서"

class UserRole(str, enum.Enum):
    ADMIN = "관리자"
    WORKER = "작업자"
    ENGINEER = "엔지니어"

class UserState(str, enum.Enum):
    PENDING = "승인 요청"
    LOGOUT = "로그아웃"
    LOGIN = "로그인"

# --- User 테이블 모델 ---

class User(Base):
    __tablename__ = "users"

    # user_id: BIGINT, PK, Auto Increment
    user_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)

    # email: VARCHAR, UNIQUE, Not Null
    email = Column(String(100), unique=True, index=True, nullable=False)

    # password: VARCHAR, Not Null (암호화된 비밀번호 저장)
    password = Column(String(255), nullable=False)

    # name: VARCHAR, Not Null
    name = Column(String(50), nullable=False)

    # department: ENUM, Not Null
    department = Column(Enum(DepartmentType), nullable=False)

    # role: ENUM, Not Null
    role = Column(Enum(UserRole), nullable=False)

    # state: ENUM, Not Null
    state = Column(Enum(UserState), default=UserState.PENDING, nullable=False)

    # created_at: TIMESTAMP, Not Null, 기본값 현재시간
    # server_default=func.now()는 DB가 직접 시간을 생성하게 합니다.
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    manuals = relationship("SavedManual", back_populates="creator")
    search_histories = relationship("SearchHistory", back_populates="user")