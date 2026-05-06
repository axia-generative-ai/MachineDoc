from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.crud import crud_user
from app.schemas.user import UserCreate, UserUpdateByAdmin, UserUpdateMe

def register_new_user(db: Session, obj_in: UserCreate):
    # 1. 이메일 중복 체크 (비즈니스 로직)
    user = crud_user.get_user_by_email(db, email=obj_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용 중인 이메일입니다."
        )
    
    # 2. 회원가입 진행 (CRUD 호출)
    new_user = crud_user.create_user(db, obj_in=obj_in)
    return {"detail": f"사용자(ID: {new_user.name})의 회원가입이 성공적으로 완료되었습니다."}

def update_user_info(db: Session, user_id: int, obj_in: UserUpdateByAdmin):
    # 1. 수정할 유저 존재 확인
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="해당 사용자를 찾을 수 없습니다."
        )
    
    # 2. CRUD 호출하여 정보 업데이트
    return crud_user.update_user_by_admin(db, db_user=db_user, obj_in=obj_in)

def delete_user_account(db: Session, target_user_id: int, admin_user_id: int):
    # 1. 삭제할 유저 존재 확인
    db_user = db.query(User).filter(User.user_id == target_user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="해당 사용자를 찾을 수 없습니다."
        )
    
    # 2. 자기 자신 삭제 방지 안전장치
    if admin_user_id == target_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="관리자 본인의 계정은 삭제할 수 없습니다."
        )
    
    # 3. 유저 삭제 실행
    crud_user.delete_user(db, user_id=target_user_id)
    return {"detail": f"사용자(ID: {target_user_id}) 삭제가 성공적으로 완료되었습니다."}

def get_pending_user_list(db: Session):
    """
    승인 대기 중인 사용자 목록을 반환합니다.
    """
    # 추가적인 비즈니스 로직(예: 특정 부서만 필터링 등)이 필요하면 여기서 처리합니다.
    return crud_user.get_pending_users(db)

def update_my_info(db: Session, current_user: User, obj_in: UserUpdateMe):
    """
    현재 로그인된 유저의 정보를 수정합니다.
    """
    # 수정 요청온 데이터 중 값이 있는 것만 추출
    update_data = obj_in.model_dump(exclude_unset=True)
    
    # CRUD 호출
    return crud_user.update_user(db, db_user=current_user, obj_in=update_data)

def get_user_list(db: Session, skip: int, limit: int):
    """
    전체 사용자 목록을 조회하는 비즈니스 로직입니다.
    """
    return crud_user.get_users(db, skip=skip, limit=limit)