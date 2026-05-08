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

router = APIRouter(prefix="/api/v1", tags=["anomaly"])
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


@router.post("/anomaly", response_model=BackendAnomalyResponse)
def analyze(req: BackendAnomalyRequest) -> BackendAnomalyResponse:
    """Backend-facing endpoint."""
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


@router.post("/anomaly/full", response_model=AnomalyResponse)
def analyze_full(payload: SensorLog) -> AnomalyResponse:
    """Internal endpoint exposing the full AnomalyResponse."""
    return _run_analyze(payload)
