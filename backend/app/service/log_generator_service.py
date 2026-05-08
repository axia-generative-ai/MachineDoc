import random
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional

from app.models.log import DataType, LogStatus
from app.models.equipment import Equipment
from app.schemas.log import EquipmentLogCreate
from app.schemas.threshold import ThresholdResponse
from app.crud.crud_equipment import equipment_repository
from app.crud.crud_threshold import threshold_repository
from app.crud.crud_log import log_repository
from app.service.notification_service import notification_service

class LogGeneratorService:
    async def create_virtual_log_by_name(self, db: Session, equipment_name: str):
        # 1. 설비 정보 조회
        equipment = equipment_repository.get_by_name(db, name=equipment_name)
        if not equipment:
            raise HTTPException(status_code=404, detail=f"설비 '{equipment_name}'을 찾을 수 없습니다.")

        # 2. 가상 데이터 생성 (타입 결정 및 무작위 값)
        data_type = random.choice(list(DataType))
        value = self._generate_random_value(data_type)

        # 3. 임계값 조회 CRUD 사용 (분리 완료)
        threshold = threshold_repository.get_by_equipment_and_type(
            db, 
            equipment_id=equipment.equipment_id, 
            data_type=data_type
        )

        # 4. 상태 분석 (DB 임계값 기반)
        status = self._analyze_log_status(value, threshold)

        # 5. 로그 생성 및 DB 저장
        log_in = EquipmentLogCreate(
            equipment_id=equipment.equipment_id,
            data_type=data_type,
            value=value,
            status=status,
            occurred_at=datetime.now()
        )

        return await self._process_log_save(db, log_in, equipment)

    def _analyze_log_status(self, value: float, threshold: Optional[ThresholdResponse]) -> LogStatus:
            """스키마(ThresholdResponse)를 바탕으로 상태 판별"""
            if not threshold:
                return LogStatus.NORMAL

            # 스키마 객체의 속성에 접근하여 비교
            if value >= threshold.error_threshold:
                return LogStatus.ERROR
            elif value >= threshold.warning_threshold:
                return LogStatus.WARNING
            return LogStatus.NORMAL

    def _generate_random_value(self, data_type: DataType) -> float:
        """현실적인 데이터 범위를 생성"""
        if data_type == DataType.TEMPERATURE:
            return round(random.uniform(20.0, 110.0), 2)  # 20~110도
        return round(random.uniform(100.0, 1300.0), 2)    # 100~1300Hz

    async def _process_log_save(self, db: Session, log_in: EquipmentLogCreate, equipment):
        """최종 저장 및 이상 감지 알림 로직 연동"""
        new_log = log_repository.create(db, obj_in=log_in)
        
        if new_log.status != LogStatus.NORMAL:
            await self._trigger_anomaly_actions(db, new_log, equipment)
            
        return new_log

    async def _trigger_anomaly_actions(self, db: Session, log, equipment):
        """이상치 발생 시 수행할 액션 (추후 Discord 알림 등 연결)"""
        await notification_service.process_anomaly_notification(db, log, equipment)

log_generator_service = LogGeneratorService()