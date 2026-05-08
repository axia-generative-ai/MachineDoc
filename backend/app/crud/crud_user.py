from sqlalchemy.orm import Session
from app.models.user import User, UserState
from app.schemas.user import UserCreate, UserUpdateByAdmin
from app.core.security import get_password_hash # 아까 만든 암호화 함수

class UserRepository:
    # 이메일로 중복 사용자 확인
    def get_user_by_email(self, db: Session, email: str):
        return db.query(User).filter(User.email == email).first()

    # 회원 생성 (Spring의 Repository.save 역할)
    def create_user(self, db: Session, obj_in: UserCreate):
        # 비밀번호 암호화
        hashed_pwd = get_password_hash(obj_in.password)
        
        # DB 모델 객체 생성
        db_obj = User(
            email=obj_in.email,
            password=hashed_pwd,
            name=obj_in.name,
            department=obj_in.department,
            role=obj_in.role
            # state는 모델에서 default='승인 요청'으로 설정했으므로 생략 가능
        )
        
        db.add(db_obj)
        db.commit()      # DB 반영
        db.refresh(db_obj) # 생성된 ID 등 최신 정보 로드
        return db_obj

    def update_user_by_admin(self, db: Session, db_user: User, obj_in: UserUpdateByAdmin):
        # 넘겨받은 데이터 중 값이 있는 것만 골라서 업데이트
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def delete_user(self, db: Session, user_id: int):
        user = db.query(User).filter(User.user_id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
        return user

    def get_pending_users(self, db: Session):
        """
        상태가 PENDING인 모든 사용자 목록을 조회합니다.
        """
        return db.query(User).filter(User.state == UserState.PENDING).all()

    def update_user(self, db: Session, db_user: User, obj_in: dict):
        """
        유저 객체와 수정할 데이터(dict)를 받아 DB에 반영합니다.
        """
        for field, value in obj_in.items():
            if field == "password":
                value = get_password_hash(value) # 비밀번호는 반드시 해싱
            setattr(db_user, field, value)
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def get_users(self, db: Session, skip: int = 0, limit: int = 100):
        """
        데이터베이스에서 사용자 목록을 페이지네이션하여 조회합니다.
        - skip: 건너뛸 데이터 개수
        - limit: 한 번에 가져올 최대 데이터 개수
        """
        return db.query(User).offset(skip).limit(limit).all()

user_repository = UserRepository()