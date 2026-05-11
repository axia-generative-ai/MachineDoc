"""Request/response models for POST /api/v1/ingest.

ai-service authors this contract; backend follows it. Locked at the
2026-05-08 integration sync.

Backend posts a multipart upload (`file`) plus form fields. ai-service
runs the synchronous v2 ingest pipeline (chunk + embed + persist) and
returns the indexing summary plus the distinct list of fault codes
detected in the manual. Backend then inserts those codes into its own
`error_code` table (E-3 sync model).
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class IngestResponse(BaseModel):
    """Result of a synchronous PDF ingest.

    The shape backend should parse:
      - manual_id / equipment_id echo back the form fields, so backend
        can correlate the response with its own DB row.
      - sections_indexed / chunks_indexed are operational counters
        (useful for observability + quick "did anything land" check).
      - error_codes is the distinct list of fault codes ai-service
        extracted from this manual's chunks. Backend should INSERT each
        as a row in its `error_code` table with manual_id pointing at
        the saved_manual entry it just created.
      - elapsed_s is how long the synchronous call took on the server
        side (for backend timeout budgeting).
    """

    manual_id: str = Field(..., description="Manual slug ai-service indexes by, echoed from request.")
    equipment_id: str = Field(..., description="Equipment slug, echoed from request.")
    source_filename: str = Field(..., description="Original uploaded filename.")
    sections_indexed: int = Field(..., ge=0, description="Parent sections inserted into manual_sections.")
    chunks_indexed: int = Field(..., ge=0, description="Child chunks inserted into manual_chunks_v2.")
    error_codes: list[str] = Field(
        default_factory=list,
        description="Distinct fault/error codes detected in this manual. Backend syncs these into its error_code table.",
    )
    elapsed_s: float = Field(..., ge=0.0, description="Server-side ingest wall time in seconds.")
