import random
import logging
from datetime import datetime
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.crud.crud_equipment import equipment_repository
from app.crud.crud_threshold import threshold_repository
from app.crud.crud_log import log_repository
from app.models.log import DataType, LogStatus
from app.schemas.log import EquipmentLogCreate
from app.schemas.threshold import ThresholdResponse
from app.service.notification_service import notification_service

log = logging.getLogger(__name__)

# 가상 로그 생성 + 이상 감지는 백엔드에서 threshold 비교만 수행한다 (로컬, LLM 미사용).
# ai-service 의 POST /api/v1/anomaly 엔드포인트(BackendAnomalyRequest/Response)는
# 별도 통합 단계에서 호출 옵션으로 추가될 수 있으나, 현재 데모 경로에서는 호출하지 않는다.
# LLM 분석은 오류코드 검색(/search/code → ai-service /api/v1/search) 흐름에서만 일어난다.
class LogGeneratorService:
    async def create_virtual_log_by_name(self, db: Session, equipment_name: str):
        equipment = equipment_repository.get_by_name(db, name=equipment_name)
        if not equipment:
            raise HTTPException(status_code=404, detail=f"설비 '{equipment_name}'을 찾을 수 없습니다.")

        data_type = random.choice(list(DataType))
        value = self._generate_random_value(data_type)

        threshold = threshold_repository.get_by_equipment_and_type(
            db,
            equipment_id=equipment.equipment_id,
            data_type=data_type
        )

        status = self._analyze_log_status(value, threshold)

        log_in = EquipmentLogCreate(
            equipment_id=equipment.equipment_id,
            data_type=data_type,
            value=value,
            status=status,
            occurred_at=datetime.now()
        )

        new_log = await self._process_log_save(db, log_in, equipment)
        return new_log

    def _analyze_log_status(self, value: float, threshold: Optional[ThresholdResponse]) -> LogStatus:
        if not threshold:
            return LogStatus.NORMAL
        if value >= threshold.error_threshold:
            return LogStatus.ERROR
        elif value >= threshold.warning_threshold:
            return LogStatus.WARNING
        return LogStatus.NORMAL

    def _generate_random_value(self, data_type: DataType) -> float:
        if data_type == DataType.TEMPERATURE:
            return round(random.uniform(20.0, 110.0), 2)
        return round(random.uniform(100.0, 1300.0), 2)

    async def _process_log_save(self, db: Session, log_in: EquipmentLogCreate, equipment):
        new_log = log_repository.create(db, obj_in=log_in)
        if new_log.status != LogStatus.NORMAL:
            await notification_service.process_anomaly_notification(db, new_log, equipment)
        return new_log


log_generator_service = LogGeneratorService()
