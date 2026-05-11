"""Request/response models for the manual recommendation endpoint.

Used by backend `saved_manual_service.get_equipment_manual` when the
DB-side category lookup returns nothing — backend delegates to
`/api/v1/manuals/recommend` to surface manuals from the indexed corpus.

No LLM call (latency budget: retrieval-only, ~1s).
"""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class RecommendRequest(BaseModel):
    """At least one of equipment_id / category / query must be provided."""

    equipment_id: str | None = Field(
        default=None,
        description="Backend equipment_code (e.g. 'EQ-MOTOR-001'). Routed via internal mapping to indexed manuals.",
    )
    category: str | None = Field(
        default=None,
        description="Free-text category from backend (e.g. '점검', '수리').",
    )
    query: str | None = Field(
        default=None,
        description="Optional free-text query to widen / refine the search.",
    )
    top_k: int = Field(default=5, ge=1, le=20)

    @model_validator(mode="after")
    def _at_least_one(self) -> "RecommendRequest":
        if not (self.equipment_id or self.category or self.query):
            raise ValueError("At least one of equipment_id / category / query is required.")
        return self


class RecommendedManual(BaseModel):
    manual_id: str = Field(..., description="ai-service slug (e.g. 'abb_irb_troubleshooting').")
    title: str = Field(..., description="Filename or human-friendly title.")
    equipment_id: str = Field(..., description="ai-service equipment slug (e.g. 'eq_abb_irb').")
    page: int = Field(..., description="Best-match page from the manual.")
    excerpt: str = Field(..., description="Short snippet (~200 chars) from the matching chunk.")
    similarity: float = Field(..., description="Hybrid retrieval score; higher is better.")


class RecommendResponse(BaseModel):
    query_used: str = Field(..., description="Composed query string actually sent to retrieval.")
    routed_equipment_id: str | None = Field(
        default=None,
        description="If a backend EQ-XXX-NNN was mapped to an indexed manual, the mapped slug. None = corpus-wide search.",
    )
    results: list[RecommendedManual]
