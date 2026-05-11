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

router = APIRouter(prefix="/api/v1", tags=["오류코드 검색"])
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


@router.post(
    "/search",
    response_model=BackendSearchResponse,
    summary="오류코드 검색 (백엔드용)",
    description=(
        "오류코드를 받아 관련 매뉴얼을 RAG로 검색하고 한국어 조치 절차를 생성합니다.\n\n"
        "**요청**: `{error_code, equipment_id?}`\n\n"
        "**응답**: `{status, analysis, solution}` 세 필드 한국어 문자열. "
        "백엔드가 추가 변환 없이 프런트엔드에 그대로 전달 가능.\n\n"
        "- `status`: `success` | `no_match` | `error`\n"
        "- `analysis`: LLM이 정리한 원인 분석 (한국어, 출처 페이지 인용 포함)\n"
        "- `solution`: 단계별 조치 절차 (한 줄당 1단계, 출처 명시)"
    ),
)
def search(req: BackendSearchRequest) -> BackendSearchResponse:
    """오류코드 → 매뉴얼 조치 절차. 백엔드 contract 고정."""
    internal = _run_search(
        query=req.error_code,
        equipment_id=req.equipment_id,
        top_k=None,
    )
    return _to_backend_response(internal)


@router.post(
    "/search/full",
    response_model=SearchResponse,
    summary="자유 query 검색 (내부 디버깅용)",
    description=(
        "자유 텍스트 query로 매뉴얼을 검색하고 raw chunks + LLM 답변을 모두 반환합니다.\n\n"
        "내부 디버깅 / KPI eval 러너 전용. 백엔드는 호출하지 않습니다.\n\n"
        "**응답**: `steps[]`, `raw_chunks[]`, `answer_text`, `fallback`, `latency_ms`."
    ),
)
def search_full(req: SearchRequest) -> SearchResponse:
    """디버깅용 — full SearchResponse 노출."""
    return _run_search(
        query=req.query,
        equipment_id=req.equipment_id,
        top_k=req.top_k,
    )
