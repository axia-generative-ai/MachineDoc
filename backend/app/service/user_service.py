from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud.crud_user import user_repository
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdateByAdmin, UserUpdateMe


class UserService:
    def register_new_user(self, db: Session, obj_in: UserCreate):
        user = user_repository.get_user_by_email(db, email=obj_in.email)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 사용 중인 이메일입니다.",
            )

        new_user = user_repository.create_user(db, obj_in=obj_in)
        return {"detail": f"사용자 ID: {new_user.name}) 회원가입이 성공적으로 완료되었습니다."}

    def update_user_info(
        self,
        db: Session,
        user_id: int,
        obj_in: UserUpdateByAdmin,
        admin_user_id: int,
    ):
        db_user = db.query(User).filter(User.user_id == user_id).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 사용자를 찾을 수 없습니다.",
            )

        if admin_user_id == user_id and obj_in.role is not None and obj_in.role != db_user.role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="관리자는 본인 계정의 권한을 변경할 수 없습니다.",
            )

        return user_repository.update_user_by_admin(db, db_user=db_user, obj_in=obj_in)

    def delete_user_account(self, db: Session, target_user_id: int, admin_user_id: int):
        db_user = db.query(User).filter(User.user_id == target_user_id).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 사용자를 찾을 수 없습니다.",
            )

        if admin_user_id == target_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="관리자 본인 계정은 삭제할 수 없습니다.",
            )

        user_repository.delete_user(db, user_id=target_user_id)
        return {"detail": f"사용자 ID: {target_user_id}) 삭제가 성공적으로 완료되었습니다."}

    def get_pending_user_list(self, db: Session):
        return user_repository.get_pending_users(db)

    def update_my_info(self, db: Session, current_user: User, obj_in: UserUpdateMe):
        update_data = obj_in.model_dump(exclude_unset=True)
        return user_repository.update_user(db, db_user=current_user, obj_in=update_data)

    def get_user_list(self, db: Session, skip: int, limit: int):
        return user_repository.get_users(db, skip=skip, limit=limit)


user_service = UserService()
