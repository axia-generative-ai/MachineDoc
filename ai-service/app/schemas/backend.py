"""Backend-facing request/response shapes.

Backend's `core/ai_client.py` and `service/search_service.py` were
written first against a mock; ai-service conforms to that mock's shape
(2026-05-08 integration sync, decision B). When the contract evolves
the change happens here, not in the internal SearchResponse.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class BackendSearchRequest(BaseModel):
    """Backend posts an error code as a single field.

    `equipment_id` is reserved for future use — backend is not sending
    it today, but accepting it now means we don't need a contract bump
    when they do.
    """

    error_code: str = Field(..., min_length=1)
    equipment_id: str | None = None


SearchStatus = Literal["success", "no_match", "error"]


class BackendSearchResponse(BaseModel):
    """Shape backend's mock currently produces.

    `status` lets backend distinguish a real answer from the fallback
    branch ("관련 매뉴얼을 찾지 못했습니다"). `analysis` is the model's
    Korean explanation; `solution` is the numbered action list collapsed
    into a single string ready for display.
    """

    status: SearchStatus
    analysis: str
    solution: str


class BackendAnomalyRequest(BaseModel):
    """Authored ai-side per the 2026-05-08 sync (G-1).

    Mirrors the existing internal SensorLog shape so backend doesn't
    need to invent a new payload format and the rule engine + LLM
    analyzer get exactly what they already expect:
      - `equipment_id`: required, scopes the rule check.
      - `timestamp`: ISO 8601, when the readings were captured.
      - `readings`: free-form metric → numeric value map (vibration,
        temperature, current, ...). The rule engine indexes by metric
        name, so backend just needs to forward whatever the sensor
        layer reports.
    """

    equipment_id: str = Field(..., min_length=1)
    timestamp: str = Field(..., description="ISO 8601 timestamp of the reading window.")
    readings: dict[str, float] = Field(default_factory=dict)


class BackendAnomalyResponse(BaseModel):
    """Same three-string shape as BackendSearchResponse for parser symmetry.

    `status`:
      - `정상` (normal) — no rule fired, LLM concurs
      - `주의` (warning) — soft signal worth surfacing
      - `이상` (anomaly) — rule fired or LLM flagged a fault
      - `error` — pipeline failed; analysis carries the reason

    Note: the Korean status strings come straight from the existing
    AnomalyResponse so the rule-engine output and the backend response
    stay aligned. Backend can switch on these values directly.
    """

    status: Literal["정상", "주의", "이상", "error"]
    analysis: str
    solution: str
