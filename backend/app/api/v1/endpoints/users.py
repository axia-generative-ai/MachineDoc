from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas import user as user_schema
from app.models.user import User
from app.service.user_service import user_service
router = APIRouter()

@router.get(
    "/", 
    summary="전체 사용자 목록 조회 (관리자 전용)",
    response_model=List[user_schema.UserRead]
)
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, description="건너뛸 데이터 수"),
    limit: int = Query(100, le=100, description="최대 조회 데이터 수"),
    admin_user: User = Depends(deps.get_current_admin_user)
):
    """
    시스템에 등록된 모든 사용자의 정보를 리스트 형태로 조회합니다.
    - **관리자(ADMIN) 권한**이 있는 사용자만 호출할 수 있습니다.
    - 대량의 데이터를 방지하기 위해 **페이지네이션**을 지원합니다.
    - **skip**: 시작 지점 (기본값: 0)
    - **limit**: 조회할 개수 (기본값: 100, 최대: 100)
    - 응답 데이터에는 비밀번호와 같은 민감 정보가 제외된 **UserRead** 형식이 적용됩니다.
    """
    return user_service.get_user_list(db, skip=skip, limit=limit)

@router.get(
    "/pending", 
    summary="승인 대기 사용자 목록 조회 (관리자 전용)",
    response_model=List[user_schema.UserRead]
)
def read_pending_users(
    db: Session = Depends(deps.get_db),
    admin_user: User = Depends(deps.get_current_admin_user)
):
    """
    관리자 권한으로 시스템 접속 승인을 기다리고 있는(**PENDING** 상태) 사용자 목록을 조회합니다.
    - 신규 회원가입 후 아직 승인되지 않은 사용자들을 한눈에 확인할 수 있습니다.
    - 결과는 **List[UserRead]** 형태로 반환됩니다.
    - 권한이 없는 일반 사용자가 호출할 경우 **403 Forbidden** 에러가 발생합니다.
    """
    return user_service.get_pending_user_list(db)

@router.patch(
    "/me", 
    summary="내 정보 수정",
    response_model=user_schema.UserRead
)
def update_user_me(
    obj_in: user_schema.UserUpdateMe,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user) # 본인 확인
):
    """
    로그인한 사용자 본인의 정보를 수정합니다.
    - **이름**과 **비밀번호**를 변경할 수 있습니다.
    - 수정하고 싶은 필드만 보내면 해당 필드만 업데이트됩니다.
    - 관리자 권한 없이 일반 사용자도 자신의 토큰만 있다면 가능합니다.
    """
    return user_service.update_my_info(db, current_user=current_user, obj_in=obj_in)

@router.patch(
    "/{user_id}", 
    summary="사용자 정보 수정 (관리자 전용)",
    response_model=user_schema.UserRead # 반환 스키마 설정
)
def update_user(
    user_id: int,
    obj_in: user_schema.UserUpdateByAdmin,
    db: Session = Depends(deps.get_db),
    admin_user: User = Depends(deps.get_current_admin_user)
):
    """
    관리자 권한으로 특정 사용자의 정보를 수정합니다.
    - **이름, 부서, 역할, 상태**를 선택적으로 수정할 수 있습니다.
    - 수정이 필요한 필드만 데이터에 포함하여 요청하세요.
    - 존재하지 않는 user_id인 경우 404 에러를 반환합니다.
    """
    return user_service.update_user_info(db, user_id=user_id, obj_in=obj_in)

@router.delete(
    "/{user_id}", 
    summary="사용자 계정 삭제 (관리자 전용)",
)
def delete_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    admin_user: User = Depends(deps.get_current_admin_user)
):
    """
    관리자 권한으로 특정 사용자의 계정을 완전히 삭제합니다.
    - 삭제된 데이터는 복구할 수 없으니 신중하게 사용하세요.
    - **안전장치**: 관리자 본인의 계정은 이 API로 삭제할 수 없습니다.
    - 성공 시 삭제 완료 메시지를 반환합니다.
    """
    return user_service.delete_user_account(
        db, 
        target_user_id=user_id, 
        admin_user_id=admin_user.user_id
    )

