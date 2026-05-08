from fastapi import APIRouter, Depends, HTTPException
from app.models.user import User
from sqlalchemy.orm import Session
from app.api import deps
from app.db.session import get_db
from app.service.log_generator_service import log_generator_service
from app.schemas.log import EquipmentLogResponse

router = APIRouter()

@router.post(
    "/virtual/{equipment_name}", 
    response_model=EquipmentLogResponse,
    summary="가상 로그 생성 및 분석",
    responses={
        200: {"description": "로그 생성 성공 (이상 징후 발생 시 웹소켓 알림 동시 발송)"},
        401: {"description": "인증되지 않은 사용자 (로그인 필요)"},
        404: {"description": "해당 이름의 설비를 찾을 수 없음"},
        500: {"description": "서버 내부 오류 (임계값 미설정 등)"}
    }
)
async def create_virtual_log(
    equipment_name: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    ## 🏭 테스트 가능한 설비 리스트
    아래 설비 코드 중 하나를 복사하여 equipment_name에 입력하세요:

    | 설비명 (Code) | 위치 | 설명 |
    |:---|:---|:---|
    | **EQ-MOTOR-001** | Line A | 정밀 모터 (온도/진동 기준 엄격) |
    | **EQ-CONVEYOR-002** | Line A | 표준 컨베이어 |
    | **EQ-PRESS-003** | Line B | 고온/고진동 프레스 |
    | **EQ-ROBOT-004** | Line B | 정밀 로봇 팔 |
    | **EQ-WELDING-005** | Line C | 용접기 (열 발생 잦음) |

    ### 🔍 주요 기능
    1. **데이터 생성**: 온도(20~110°C) 또는 진동(100~1300Hz) 데이터를 무작위로 생성합니다.
    2. **상태 판별**: 해당 설비에 설정된 임계값(Threshold)을 기준으로 **정상/경고/위험** 상태를 판별합니다.
    3. **이상 감지 알림 (WebSocket)**: 
        - 상태가 **'경고'** 또는 **'위험'**일 경우, Notification을 생성하여 DB에 저장합니다.
        - 연결된 모든 클라이언트에게 웹소켓(ANOMALY_DETECTED 이벤트)으로 실시간 알림을 전송합니다.
    4. **설비 상태 업데이트**: 상태가 **'위험'**일 경우, 해당 설비의 가동 상태를 자동으로 ERROR로 변경합니다.
    
    ### 🔒 보안:
    - 이 API는 **로그인한 사용자**만 호출할 수 있습니다.
    """
    try:
        new_log = await log_generator_service.create_virtual_log_by_name(db, equipment_name)
        return new_log
    except HTTPException as e:
        raise e
    except Exception as e:
        # 예상치 못한 에러 처리
        raise HTTPException(status_code=500, detail=f"가상 로그 생성 중 오류 발생: {str(e)}")