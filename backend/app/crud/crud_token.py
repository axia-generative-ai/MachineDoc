from sqlalchemy.orm import Session
from app.models.refresh_token import RefreshToken  # DB 모델
from app.schemas.token import RefreshTokenCreate

class TokenRepositoy:
    def create_or_update_refresh_token(self, db: Session, obj_in: RefreshTokenCreate):
        # 1. 해당 유저에게 기존에 발급된 토큰이 있는지 확인
        db_obj = db.query(RefreshToken).filter(RefreshToken.user_id == obj_in.user_id).first()
        
        if db_obj:
            # 2. 있다면 새로운 토큰과 만료 시간으로 업데이트
            db_obj.token = obj_in.token
            db_obj.expires_at = obj_in.expires_at
        else:
            # 3. 없다면 새로 생성
            db_obj = RefreshToken(
                user_id=obj_in.user_id,
                token=obj_in.token,
                expires_at=obj_in.expires_at
            )
            db.add(db_obj)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete_refresh_token(self, db: Session, user_id: int):
        db.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()
        db.commit()

token_repository = TokenRepositoy()