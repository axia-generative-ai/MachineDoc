"""POST /api/v1/search — action-guide generation endpoint.

Two shapes are exposed here:

- `POST /api/v1/search`        (backend-facing, locked 2026-05-08)
    Accepts `{error_code, equipment_id?}` and returns
    `{status, analysis, solution}`. The internal SearchResponse is
    flattened into Korean strings so backend can pass the result
    straight through to its frontend without further parsing.

- `POST /api/v1/search/full`   (internal / debugging)
    Accepts the rich SearchRequest and returns the full SearchResponse
    (steps, raw_chunks, latency_ms, ...). Useful for the eval runner
    and for ad-hoc inspection — backend should not call this.

Picks the RAG pipeline based on `settings.pipeline_version`:
  - "v1" → RagPipeline (legacy vector-only)
  - "v2" → RagPipelineV2 (hybrid retrieval + reranker, Top-3 96%)
"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Protocol

from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.pipelines.rag import RagPipeline
from app.pipelines.rag_v2 import RagPipelineV2
from app.schemas.backend import BackendSearchRequest, BackendSearchResponse
from app.schemas.search import SearchRequest, SearchResponse

router = APIRouter(prefix="/api/v1", tags=["search"])
log = logging.getLogger(__name__)


class _SearchPipeline(Protocol):
    def search(
        self,
        query: str,
        *,
        equipment_id: str | None = None,
        top_k: int | None = None,
    ) -> SearchResponse: ...


@lru_cache(maxsize=1)
def _pipeline() -> _SearchPipeline:
    settings = get_settings()
    if settings.pipeline_version == "v2":
        log.info("RAG pipeline=v2 (RagPipelineV2)")
        return RagPipelineV2.build(settings)
    log.info("RAG pipeline=v1 (RagPipeline)")
    return RagPipeline.build(settings)


def _run_search(query: str, equipment_id: str | None, top_k: int | None) -> SearchResponse:
    try:
        return _pipeline().search(query, equipment_id=equipment_id, top_k=top_k)
    except ConnectionError as exc:
        log.exception("LLM/embedding backend unreachable")
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _to_backend_response(internal: SearchResponse) -> BackendSearchResponse:
    """Flatten a rich SearchResponse into backend's three Korean strings.

    `analysis` keeps the LLM's full normalized answer (already Korean).
    `solution` collapses the numbered steps into a single string the
    frontend can drop into a textarea or detail panel without further
    parsing. Empty steps -> empty string (frontend can decide what to
    show).
    """
    if internal.fallback or not internal.steps:
        return BackendSearchResponse(
            status="no_match",
            analysis=internal.answer_text or "관련 매뉴얼을 찾지 못했습니다.",
            solution="",
        )

    solution_lines = []
    for step in internal.steps:
        line = f"{step.order}. {step.action}"
        if step.source:
            line += f" (출처: {step.source.manual} p{step.source.page})"
        solution_lines.append(line)

    return BackendSearchResponse(
        status="success",
        analysis=internal.answer_text,
        solution="\n".join(solution_lines),
    )


@router.post("/search", response_model=BackendSearchResponse)
def search(req: BackendSearchRequest) -> BackendSearchResponse:
    """Backend-facing endpoint. See module docstring for shape."""
    internal = _run_search(
        query=req.error_code,
        equipment_id=req.equipment_id,
        top_k=None,
    )
    return _to_backend_response(internal)


@router.post("/search/full", response_model=SearchResponse)
def search_full(req: SearchRequest) -> SearchResponse:
    """Internal endpoint exposing the full SearchResponse for debugging."""
    return _run_search(
        query=req.query,
        equipment_id=req.equipment_id,
        top_k=req.top_k,
    )
