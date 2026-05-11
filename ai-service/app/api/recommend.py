"""POST /api/v1/manuals/recommend — manual recommendation endpoint.

Backend `saved_manual_service.get_equipment_manual` falls through to
this endpoint when its DB-side category lookup returns nothing.
Backend can also call this proactively if it wants AI-side ranking.

Retrieval-only (no LLM). Latency budget ~1s.
Reuses HybridRetriever (PreFilter + BM25 + Vector + RRF + reranker).
"""

from __future__ import annotations

import logging
from functools import lru_cache

from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.pipelines.anomaly import _EQUIPMENT_MANUAL_MAP
from app.pipelines.rag_v2 import RagPipelineV2
from app.pipelines.retrieval_v2 import HybridRetriever
from app.schemas.recommend import (
    RecommendedManual,
    RecommendRequest,
    RecommendResponse,
)

router = APIRouter(prefix="/api/v1", tags=["매뉴얼 추천"])
log = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _retriever() -> HybridRetriever:
    """Reuse the v2 pipeline's retriever (PreFilter + BM25 + Vector + RRF + reranker)."""
    settings = get_settings()
    pipeline = RagPipelineV2.build(settings)
    return pipeline.retriever


def _compose_query(req: RecommendRequest) -> str:
    """Build a free-text retrieval query from whatever fields backend sent."""
    parts: list[str] = []
    if req.query:
        parts.append(req.query)
    if req.category:
        parts.append(req.category)
    if req.equipment_id:
        # Pass the raw backend code too — even if the mapping resolves
        # the equipment filter, the literal string can boost BM25 if
        # the user's category text alone is generic ("점검", "수리").
        parts.append(req.equipment_id)
    return " ".join(parts).strip()


def _excerpt(chunk_text: str, limit: int = 200) -> str:
    text = " ".join(chunk_text.split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


@router.post(
    "/manuals/recommend",
    response_model=RecommendResponse,
    summary="설비/카테고리 기반 매뉴얼 추천",
    description=(
        "백엔드 `saved_manual_service`가 DB-side 카테고리 검색에서 0건일 때 호출하는 fallback. "
        "AI 인덱스에서 관련 매뉴얼을 검색해 매뉴얼 메타 + 발췌 + 유사도 점수를 반환합니다.\n\n"
        "**요청**: `equipment_id`, `category`, `query` 중 **하나 이상** 필수. 셋 다 비면 422.\n"
        "- `equipment_id`: 백엔드 `equipment_code` (예: `EQ-MOTOR-001`). 내부 매핑으로 적절한 매뉴얼로 라우팅.\n"
        "- `category`: 자유 텍스트 (`점검`, `수리` 등)\n"
        "- `query`: 추가 검색어\n"
        "- `top_k`: 1~20, 기본 5\n\n"
        "**응답**: `{query_used, routed_equipment_id, results[]}`\n\n"
        "동일 매뉴얼이 여러 chunk로 떠도 매뉴얼별 1건만 dedupe해서 반환합니다.\n\n"
        "LLM 호출 없이 hybrid retrieval만 사용 (평균 응답 ~1초)."
    ),
)
def recommend_manuals(req: RecommendRequest) -> RecommendResponse:
    routed = _EQUIPMENT_MANUAL_MAP.get(req.equipment_id) if req.equipment_id else None
    query = _compose_query(req)
    if not query:
        raise HTTPException(status_code=400, detail="empty query after composition")

    try:
        hits = _retriever().retrieve(
            query,
            equipment_id=routed,
            final_k=req.top_k,
        )
    except ConnectionError as exc:
        log.exception("retrieval backend unreachable")
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    # Dedupe by manual_id — keep the highest-scoring chunk per manual.
    # Same manual surfacing N times with slightly different chunks is
    # not useful for the "give me manuals" use case.
    seen: dict[str, RecommendedManual] = {}
    for h in hits:
        if h.manual_id in seen:
            continue
        seen[h.manual_id] = RecommendedManual(
            manual_id=h.manual_id,
            title=h.manual_id.replace("_", " "),  # filename-derived; backend can prettify
            equipment_id=h.equipment_id,
            page=h.page,
            excerpt=_excerpt(h.chunk_text),
            similarity=round(h.score, 4),
        )

    return RecommendResponse(
        query_used=query,
        routed_equipment_id=routed,
        results=list(seen.values()),
    )
