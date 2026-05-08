from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.config import config
from app.crud.crud_user import user_repository
from app.models.user import User, UserRole
from app.core.database import get_db

# 1. 토큰을 가져올 경로 설정
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보가 유효하지 않습니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 2. 토큰 해독
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 3. DB에서 유저 확인
    user = user_repository.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
        
    # 4. 최종적으로 유저 객체 반환
    return user

def get_current_admin_user(current_user: User = Depends(get_current_user)):
    """
    현재 로그인한 유저가 관리자(ADMIN)인지 확인합니다.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 작업을 수행할 권한이 없습니다. 관리자만 가능합니다."
        )
    return current_user