from fastapi import HTTPException, status, Response
from sqlalchemy.orm import Session
from app.models.user import User
from app.crud.crud_user import user_repository
from app.schemas.user import UserState
from app.crud.crud_token import token_repository
from app.schemas.token import RefreshTokenCreate
from app.core.security import verify_password, create_access_token, create_refresh_token
from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.core.config import config

class AuthService:
    # def authenticate_user(db: Session, login_data: UserLoginSchema):
    def authenticate_user(self, db, username, password):
        # 1. 사용자 조회
        # user = crud_user.get_user_by_email(db, email=login_data.email)
        user = user_repository.get_user_by_email(db, email=username)
        
        # 2. 유효성 검사 및 상태 확인
        # if not user or not verify_password(login_data.password, user.password):
        if not user or not verify_password(password, user.password):
            raise HTTPException(status_code=400, detail="이메일 또는 비밀번호가 틀렸습니다.")
        
        if user.state == UserState.PENDING:
            raise HTTPException(status_code=403, detail="관리자의 승인이 대기 중인 계정입니다.")
        
        if user.state == UserState.LOGIN:
            raise HTTPException(status_code=403, detail="이미 다른 기기에서 로그인 중인 계정입니다.")

        # 3. 상태 업데이트 (logout -> login)
        user.state = UserState.LOGIN
        
        # 4. 토큰 발급 및 리프레시 토큰 DB 저장
        token_data = {"sub": user.email}
        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(data=token_data)
        
        # 5. 기존 리프레시 토큰이 있다면 업데이트, 없다면 새로 생성
        expires_at = datetime.utcnow() + timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)
        
        # 스키마 객체 생성
        token_in = RefreshTokenCreate(
            user_id=user.user_id,
            token=refresh_token,
            expires_at=expires_at
        )
        
        # CRUD 함수 호출하여 저장 또는 업데이트
        token_repository.create_or_update_refresh_token(db, obj_in=token_in)
        
        db.commit()
        
        # 6. 프론트로 유저 정보와 토큰 전달
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user_info": {
                "email": user.email,
                "name": user.name,
                "department": user.department,
                "role": user.role,
                "state": user.state
            }
        }

    def logout_user(self, db: Session, user: User):
        # 1. 유저 상태 변경
        user.state = UserState.LOGOUT
        
        # 2. 리프레시 토큰 삭제 (crud_token 함수 활용)
        token_repository.delete_refresh_token(db, user_id=user.user_id)
        
        db.commit()
        return "로그아웃이 완료됐습니다."
    
    def refresh_access_token(self, db: Session, refresh_token: str):
        # 1. JWT 토큰 디코딩 및 검증 (서명, 만료시간 등)
        try:
            payload = jwt.decode(refresh_token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="유효하지 않은 토큰입니다."
                )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="리프레시 토큰이 만료되었거나 변조되었습니다."
            )

        # 2. DB에서 해당 리프레시 토큰 존재 여부 및 만료 확인
        db_token = token_repository.get_refresh_token_by_token(db, token=refresh_token)
        
        if not db_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="존재하지 않는 리프레시 토큰입니다."
            )
        
        if db_token.expires_at < datetime.utcnow():
            # 만료된 토큰은 DB에서 삭제 후 에러 반환
            token_repository.delete_refresh_token(db, user_id=db_token.user_id)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="리프레시 토큰이 만료되었습니다. 다시 로그인해주세요."
            )

        # 3. 새로운 액세스 토큰 생성
        new_access_token = create_access_token(data={"sub": email})

        # (선택 사항) 리프레시 토큰 회전(Rotation): 보안을 위해 리프레시 토큰도 새로 발급 가능
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
    
    def set_refresh_cookie(self, response: Response, refresh_token: str):
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,     # JS 접근 불가 (XSS 방어)
            secure=True,       # HTTPS 연결에서만 전송 (운영 환경 필수)
            samesite="lax",    # CSRF 방어 정책
            max_age=config.REFRESH_TOKEN_EXPIRE_SECONDS,
            path="/",          # 모든 경로에서 쿠키 전송
        )

auth_service = AuthService()