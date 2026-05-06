from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserLoginSchema
from app.service.user_service import register_new_user
from app.service.auth_service import authenticate_user, logout_user
from app.api.deps import get_current_user

from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

@router.post(
        "/register",
        summary="신규 회원가입",
        responses={
        400: {"description": "이메일 중복으로 인한 가입 실패"},
        422: {"description": "입력 데이터 형식이 잘못됨 (예: 이메일 형식 오류)"}
    }
)
def register_user(obj_in: UserCreate, db: Session = Depends(get_db)):
    """
    FactoryGuard 시스템에 새로운 사용자를 등록합니다.

    - **중복 검사**: 입력된 **email**이 이미 DB에 존재하는지 확인합니다. 중복 시 400 에러를 반환합니다.
    - **비밀번호 암호화**: 전달된 평문 비밀번호는 보안을 위해 **Bcrypt**로 해시화되어 저장됩니다.
    - **초기 상태(State)**: 가입 시 사용자의 초기 상태는 자동으로 **pending**(승인 대기)으로 설정됩니다. 
    - **승인 절차**: **pending** 상태의 유저는 로그인을 할 수 없으며, 관리자의 승인을 통해 **logout** 상태로 변경된 후 서비스 이용이 가능합니다.
    """
    return register_new_user(db, obj_in=obj_in)

@router.post(
        "/login",
        summary="로그인 및 토큰 발급",
        responses={
            400: {"description": "이메일 또는 비밀번호 불일치"},
            403: {"description": "승인 대기(pending) 또는 이미 로그인(login) 상태"},
            404: {"description": "존재하지 않는 사용자"}
        }
)
# def login(login_data: UserLoginSchema, db: Session = Depends(get_db)):
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends() # JSON 대신 Form으로 받기
):    
    """
    사용자의 이메일과 비밀번호를 받아 인증을 진행하고, 액세스/리프레시 토큰을 반환합니다.
    - **pending**: 승인 대기 중 (로그인 불가)
    - **logout**: 로그인 가능
    - **login**: 이미 로그인 중 (중복 로그인 차단)
    """
    # return authenticate_user(db, login_data=login_data)
    return authenticate_user(db, username=form_data.username, password=form_data.password)

@router.post("/logout", summary="로그아웃")
def logout(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user) # 토큰 검증은 여기서 자동 처리
):
    """
    현재 로그인된 사용자를 로그아웃 처리합니다.
    - DB의 사용자 상태를 **logout**으로 변경
    - 저장된 리프레시 토큰 삭제
    """
    return logout_user(db, user=current_user)