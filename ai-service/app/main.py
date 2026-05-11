from __future__ import annotations

import logging

from fastapi import FastAPI

from app.api.anomaly import router as anomaly_router
from app.api.ingest import router as ingest_router
from app.api.prompts import router as prompts_router
from app.api.recommend import router as recommend_router
from app.api.search import router as search_router
from app.config import get_settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=get_settings().log_level)

app = FastAPI(
    title="MachineDoc AI 서비스",
    version="0.1.0",
    description=(
        "스마트팩토리 설비 매뉴얼 RAG 검색과 이상감지 분석을 제공하는 AI 서비스입니다.\n\n"
        "- 오류코드 → 매뉴얼 조치 절차 검색 (`/api/v1/search`)\n"
        "- 가상 센서 로그 → 룰엔진 + LLM 이상 분석 (`/api/v1/anomaly`)\n"
        "- 매뉴얼 PDF 업로드 → 청킹/임베딩/색인 (`/api/v1/ingest`)\n"
        "- 설비/카테고리 기반 매뉴얼 추천 (`/api/v1/manuals/recommend`)\n\n"
        "백엔드는 위 4개 endpoint를 호출해 풀스택 통합을 구성합니다."
    ),
)

app.include_router(search_router)
app.include_router(anomaly_router)
app.include_router(ingest_router)
app.include_router(recommend_router)
app.include_router(prompts_router)


@app.on_event("startup")
def _warmup_embedder() -> None:
    """Page the embedding model into Ollama memory at startup.

    Without this, the *first* request after Ollama unloads the model
    (default idle timeout 5 min) pays a 2 s+ retrieval cost. The latency
    benchmark P95 fails over this exact spike. We discard the result —
    we only care that the model is hot.
    """
    try:
        from app.core.embeddings import get_embeddings

        get_embeddings().embed_query("warmup")
        logger.info("embedder warmed up at startup")
    except Exception as exc:  # noqa: BLE001 — startup must not crash the app
        logger.warning("embedder warmup failed: %s", exc)


@app.on_event("startup")
def _warmup_retrieval() -> None:
    """Build the RAG pipeline and run one dummy retrieval at startup.

    First /api/v1/search call otherwise pays: pipeline build (vector
    store, BM25 index, reranker model load to GPU) + first pgvector
    query + first reranker forward pass. That stack regularly blows past
    backend's 30 s httpx timeout → backend returns 503. LLM is skipped —
    we only warm the retriever; the LLM hot-path is paged in by the
    embedder warmup above and the first real call.
    """
    try:
        from app.api.search import _pipeline

        pipeline = _pipeline()
        retriever = getattr(pipeline, "retriever", None)
        if retriever is None:
            logger.info("retrieval warmup skipped (pipeline has no retriever)")
            return
        retriever.retrieve("warmup")
        logger.info("retrieval pipeline warmed up at startup")
    except Exception as exc:  # noqa: BLE001 — startup must not crash the app
        logger.warning("retrieval warmup failed: %s", exc)


@app.get("/health", tags=["헬스체크"], summary="liveness 확인")
def health() -> dict[str, str]:
    """서비스 가동 여부만 확인. DB / Ollama 상태는 보지 않음."""
    return {"status": "ok"}


def main() -> None:
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )


if __name__ == "__main__":
    main()
