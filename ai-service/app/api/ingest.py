"""POST /api/v1/ingest — synchronous PDF ingest endpoint.

Contract authored by ai-service per the 2026-05-08 integration sync
(D-1: shared DB, sync ingest, error codes sync via ingest response).
Backend's PDF upload handler calls this endpoint with the uploaded
bytes; ai-service indexes the PDF into manual_sections + manual_chunks_v2
and returns the list of fault codes it extracted so backend can
populate its own `error_code` table.

Large manuals (~600p) take 100s+. Backend should size its httpx
timeout accordingly.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.vectorstore import VectorStore
from app.schemas.ingest import IngestResponse
from app.services.ingest_service import ingest_pdf

router = APIRouter(prefix="/api/v1", tags=["매뉴얼 업로드"])
log = logging.getLogger(__name__)


@router.post(
    "/ingest",
    response_model=IngestResponse,
    summary="매뉴얼 PDF 업로드 + 자동 색인",
    description=(
        "PDF 파일을 받아 청킹 → 임베딩 → 벡터DB 색인까지 한 번에 처리하고, "
        "자동 추출된 오류코드 목록을 응답으로 돌려줍니다.\n\n"
        "**요청 (multipart/form-data)**:\n"
        "- `file`: PDF 파일 (텍스트 레이어 필요)\n"
        "- `manual_id`: ai-service가 색인 키로 쓸 슬러그 (예: `abb_irb_troubleshooting`)\n"
        "- `equipment_id`: 설비 슬러그 (예: `eq_abb_irb`)\n\n"
        "**응답**: `{manual_id, equipment_id, source_filename, sections_indexed, chunks_indexed, error_codes[], elapsed_s}`\n\n"
        "백엔드는 응답의 `error_codes[]`를 자기 `error_code` 테이블에 sync해야 합니다 (E-3 결정).\n\n"
        "⚠️ 동기 처리. 446페이지 매뉴얼 기준 약 113초 소요. 백엔드 timeout은 300초 권장."
    ),
)
async def ingest_manual(
    file: UploadFile = File(..., description="업로드할 PDF 파일 (텍스트 레이어 포함)"),
    manual_id: str = Form(..., description="ai-service 색인 키 슬러그 (예: 'abb_irb_troubleshooting')"),
    equipment_id: str = Form(..., description="설비 슬러그 (예: 'eq_abb_irb')"),
) -> IngestResponse:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF uploads are accepted.")

    try:
        pdf_bytes = await file.read()
    finally:
        await file.close()

    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    store = VectorStore()
    try:
        result = ingest_pdf(
            pdf_bytes,
            manual_id=manual_id,
            equipment_id=equipment_id,
            source_filename=file.filename,
            store=store,
            strategy="v2",
        )
    except Exception as exc:  # noqa: BLE001 — surface as 500 to backend
        log.exception("ingest_pdf failed", extra={"manual_id": manual_id})
        raise HTTPException(status_code=500, detail=f"ingest failed: {exc}") from exc

    error_codes = _collect_error_codes(store, manual_id=manual_id)

    # 새 매뉴얼이 색인됐으니 search 파이프라인 캐시를 무효화한다.
    # 캐시 안 비우면 PreFilter.known_codes가 stale → 새 코드가 no_match로 떨어짐.
    # 다음 /search 호출 시 lazy rebuild (첫 호출은 reranker 로드로 수 초 지연).
    _invalidate_search_pipeline_cache()

    return IngestResponse(
        manual_id=result.manual_id,
        equipment_id=result.equipment_id,
        source_filename=result.source_filename,
        sections_indexed=result.sections_inserted,
        chunks_indexed=result.chunks_inserted,
        error_codes=error_codes,
        elapsed_s=round(result.elapsed_s, 3),
    )


def _invalidate_search_pipeline_cache() -> None:
    """Drop the lru_cache holding the RAG pipeline.

    The pipeline freezes PreFilter.known_codes at build time. After a new
    manual is indexed, that whitelist is stale — codes from the new manual
    won't be recognized as identifiers and BM25 boost / equipment filter
    won't kick in, producing no_match. Clearing here forces a fresh build
    on the next /search call.

    Import inside the function to avoid a circular import at module load
    (search.py imports nothing from ingest.py, but keeping the boundary
    explicit makes the dependency direction obvious).
    """
    try:
        from app.api.search import _pipeline
        from app.pipelines.rag_v2 import invalidate_filename_cache

        _pipeline.cache_clear()
        invalidate_filename_cache()
        log.info("search pipeline + filename cache invalidated after ingest")
    except Exception:  # noqa: BLE001 — cache clear must never break ingest
        log.exception("failed to invalidate search pipeline cache")


def _collect_error_codes(store: VectorStore, *, manual_id: str) -> list[str]:
    """Distinct, sorted error codes found in this manual's sections."""
    sql = """
        SELECT DISTINCT unnest(error_codes) AS code
          FROM manual_sections
         WHERE manual_id = %s
           AND error_codes IS NOT NULL
           AND array_length(error_codes, 1) > 0
         ORDER BY code
    """
    with store._connect() as conn, conn.cursor() as cur:  # noqa: SLF001
        cur.execute(sql, (manual_id,))
        return [row[0] for row in cur.fetchall()]
