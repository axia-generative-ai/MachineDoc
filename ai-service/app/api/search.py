"""POST /api/v1/search — action-guide generation endpoint.

Picks the RAG pipeline based on `settings.pipeline_version`:
  - "v1" → RagPipeline (legacy vector-only, ABB-style synthetic eval)
  - "v2" → RagPipelineV2 (HybridRetriever + BM25 + reranker, real-manual
           Top-3 92%; see tests/eval/results/v1_vs_v2_comparison.md)

Both pipelines return the same SearchResponse schema so the API contract
is stable across the switch.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Protocol

from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.pipelines.rag import RagPipeline
from app.pipelines.rag_v2 import RagPipelineV2
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


@router.post("/search", response_model=SearchResponse)
def search(req: SearchRequest) -> SearchResponse:
    try:
        return _pipeline().search(
            req.query,
            equipment_id=req.equipment_id,
            top_k=req.top_k,
        )
    except ConnectionError as exc:
        log.exception("LLM/embedding backend unreachable")
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
