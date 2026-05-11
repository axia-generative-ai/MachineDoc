"""POST /api/v1/anomaly — anomaly analysis endpoint.

Two shapes (mirroring the search endpoint pattern):

- `POST /api/v1/anomaly`        (backend-facing)
    Accepts `{equipment_id, timestamp, readings}` and returns
    `{status, analysis, solution}` — same three-string shape as
    BackendSearchResponse so backend has one parser pattern.

- `POST /api/v1/anomaly/full`   (internal / debugging)
    Accepts SensorLog and returns the full AnomalyResponse including
    the rule_result block with triggered rules + observed values.
"""

from __future__ import annotations

import logging
from datetime import datetime
from functools import lru_cache

from fastapi import APIRouter, HTTPException

from app.pipelines.anomaly import AnomalyPipeline
from app.schemas.backend import BackendAnomalyRequest, BackendAnomalyResponse
from app.schemas.sensor_log import AnomalyResponse, SensorLog

router = APIRouter(prefix="/api/v1", tags=["이상감지"])
log = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _pipeline() -> AnomalyPipeline:
    return AnomalyPipeline.build()


def _run_analyze(payload: SensorLog) -> AnomalyResponse:
    try:
        return _pipeline().analyze(payload)
    except ConnectionError as exc:
        log.exception("LLM/embedding backend unreachable")
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _to_backend_response(internal: AnomalyResponse) -> BackendAnomalyResponse:
    """Flatten AnomalyResponse into backend's three-field shape.

    `analysis` carries the model's reasoning (probable cause). `solution`
    carries the recommended action plus, when present, the manual
    references and related error codes — frontend can show these inline
    without parsing the rule_result block.
    """
    parts: list[str] = []
    if internal.recommended_action:
        parts.append(internal.recommended_action)
    if internal.related_error_codes:
        parts.append(f"관련 코드: {', '.join(internal.related_error_codes)}")
    if internal.manual_refs:
        refs = ", ".join(f"{r.manual} p{r.page}" for r in internal.manual_refs)
        parts.append(f"참고 매뉴얼: {refs}")

    status = internal.status if internal.status in {"정상", "주의", "이상"} else "error"

    return BackendAnomalyResponse(
        status=status,  # type: ignore[arg-type]
        analysis=internal.probable_cause or internal.raw_answer,
        solution="\n".join(parts),
    )


@router.post(
    "/anomaly",
    response_model=BackendAnomalyResponse,
    summary="이상감지 분석 (백엔드용)",
    description=(
        "센서 측정값을 받아 룰엔진(1차) + LLM(2차) 분석으로 이상 여부와 조치 절차를 생성합니다.\n\n"
        "**요청**: `{equipment_id, timestamp, readings}`\n"
        "- `equipment_id`: 백엔드 `equipment_code` 그대로 (예: `EQ-MOTOR-001`)\n"
        "- `timestamp`: ISO 8601 문자열\n"
        "- `readings`: `{TEMPERATURE: float, VIBRATION: float, ...}` (백엔드 `DataType` enum 키)\n\n"
        "**응답**: `{status, analysis, solution}` 한국어 문자열.\n"
        "- `status`: `정상` | `주의` | `이상` | `error`\n"
        "- `analysis`: 추정 원인 (룰 기반 + 매뉴얼 인용)\n"
        "- `solution`: 권장 조치 + 관련 오류코드 + 참고 매뉴얼\n\n"
        "정상 케이스는 LLM 호출을 건너뛰어 즉시 응답합니다."
    ),
)
def analyze(req: BackendAnomalyRequest) -> BackendAnomalyResponse:
    """센서 측정값 → 이상 여부/원인/조치. 백엔드 contract 고정."""
    try:
        ts = datetime.fromisoformat(req.timestamp)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"invalid timestamp: {exc}") from exc

    sensor_log = SensorLog(
        equipment_id=req.equipment_id,
        timestamp=ts,
        readings=req.readings,
    )
    return _to_backend_response(_run_analyze(sensor_log))


@router.post(
    "/anomaly/full",
    response_model=AnomalyResponse,
    summary="이상감지 상세 응답 (내부 디버깅용)",
    description=(
        "발동된 룰 목록, manual_refs, related_error_codes, raw_answer, latency_ms 등 "
        "내부 상태를 모두 노출합니다. 디버깅 / 평가 전용. 백엔드는 호출하지 않습니다."
    ),
)
def analyze_full(payload: SensorLog) -> AnomalyResponse:
    """디버깅용 — full AnomalyResponse 노출."""
    return _run_analyze(payload)
