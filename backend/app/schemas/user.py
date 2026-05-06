from pydantic import BaseModel, Field, EmailStr
from app.models.user import DepartmentType, UserRole, UserState
from typing import Optional

# 1. 회원가입 시 받을 데이터 (비밀번호 포함)
class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="로그인에 사용할 이메일 주소", examples=["admin@factory.com"])
    password: str = Field(..., min_length=8, description="비밀번호 (보안을 위해 8자 이상 권장)", examples=["secure_pass123"])
    name: str = Field(..., description="사용자 실명", examples=["홍길동"])
    department: DepartmentType = Field(..., description="소속 부서 이름", examples=["라인A 보전팀"])
    role: UserRole = Field(..., description="권한(관리자, 작업자, 엔지니어)", examples=["관리자"])

# 2. 회원정보 응답 시 사용할 데이터 (비밀번호 제외!)
class UserRead(BaseModel):
    user_id: int
    email: EmailStr
    name: str
    department: DepartmentType
    role: UserRole
    state: UserState

    class Config:
        # SQLAlchemy 모델 객체를 Pydantic 객체로 자동 변환해주는 설정
        from_attributes = True

# 3. 로그인 시 받을 데이터
class UserLoginSchema(BaseModel):
    email: EmailStr = Field(..., description="사용자 계정 이메일", examples=["admin@factory.com"])
    password: str = Field(..., description="사용자 계정 비밀번호 (최소 8자 이상)", examples=["secure_pass123"])

# 4. 관리자에 의해 수정되는 일반 사용자의 데이터
class UserUpdateByAdmin(BaseModel):
    name: Optional[str] = None
    department: Optional[DepartmentType] = None
    role: Optional[UserRole] = None
    state: Optional[UserState] = None

    class Config:
        from_attributes = True

# 5. 사용자 본인에 의해 수정되는 데이터
class UserUpdateMe(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None  # 비밀번호 변경 포함
    # 이메일은 본인 확인의 기준이므로 수정을 막거나, 별도 인증 로직을 타게 하는 것이 좋습니다.

    class Config:
        from_attributes = True