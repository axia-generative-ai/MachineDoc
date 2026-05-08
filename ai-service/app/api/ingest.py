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

router = APIRouter(prefix="/api/v1", tags=["ingest"])
log = logging.getLogger(__name__)


@router.post("/ingest", response_model=IngestResponse)
async def ingest_manual(
    file: UploadFile = File(..., description="PDF binary"),
    manual_id: str = Form(..., description="Slug ai-service indexes by (e.g. 'abb_irb_troubleshooting')."),
    equipment_id: str = Form(..., description="Equipment slug (e.g. 'eq_abb_irb')."),
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

    return IngestResponse(
        manual_id=result.manual_id,
        equipment_id=result.equipment_id,
        source_filename=result.source_filename,
        sections_indexed=result.sections_inserted,
        chunks_indexed=result.chunks_inserted,
        error_codes=error_codes,
        elapsed_s=round(result.elapsed_s, 3),
    )


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
