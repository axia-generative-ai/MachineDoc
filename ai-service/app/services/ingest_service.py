"""Single-PDF ingest core.

The function `ingest_pdf` is the one entry point that any caller —
the CLI (`scripts/ingest_manuals.py`), a future upload endpoint
(`POST /api/v1/manuals`), a queue worker, a test — uses to turn one
PDF into embedded chunks persisted in the vectorstore.

Inputs are overloaded so the same function works whether the caller
has a file on disk (CLI) or raw bytes from an HTTP upload (API). The
bytes path writes to a temp file because PyMuPDF's `fitz.open` is the
chunker's input contract; rewriting the chunker to accept a stream
is out of scope for this skeleton.

`progress_cb` is a placeholder hook so a future job-tracking layer
(manual_jobs table, async worker) can subscribe to stage transitions
without touching this module again. CLI passes None.
"""

from __future__ import annotations

import logging
import tempfile
import time
from collections.abc import Callable
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Literal

from app.config import ChunkingStrategy, get_settings
from app.core.vectorstore import VectorStore
from app.pipelines.chunking import chunk_pdf
from app.pipelines.chunking_v2 import chunk_pdf_structured
from app.pipelines.embedding import embed_chunks, embed_chunks_v2
from app.services.fault_pattern_detector import (
    FaultPattern,
    detect_fault_pattern,
    extract_codes_with_pattern,
)
from app.pipelines.chunking_v2 import Section as _SectionType, Chunk as _ChunkType
import uuid as _uuid

_NUL_RE_TARGETS = ("\x00",)


def _strip_nul(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value.replace("\x00", "")
    if isinstance(value, (list, tuple)):
        cleaned = [_strip_nul(v) for v in value]
        return type(value)(cleaned)
    return value


def _build_table_row_sections(
    pattern: FaultPattern,
    *,
    manual_id: str,
    equipment_id: str,
    source_filename: str,
) -> tuple[list, list]:
    """Convert detector-extracted fault rows into Section + Chunk pairs.

    Each row becomes:
      - Section(section_type="table", heading_path=("Fault Codes", code),
                text=row_joined_text, error_codes=(code,))
      - Chunk(parent_section_id=that section, chunk_index=0,
              chunk_text=row_joined_text)

    The row text already contains code + name + cause + remedy joined by
    newlines, so a single chunk per row is sufficient (and matches the
    user's mental model of "one fault = one entry").
    """
    sections = []
    chunks = []
    seen: set[str] = set()
    for row in pattern.rows:
        if row.code in seen:
            continue
        seen.add(row.code)
        text = row.text or row.code
        # Prefix the row text with the code as a heading so BM25 / vector
        # both have multiple anchor points for the identifier.
        full_text = f"{row.code}\n{text}" if not text.lstrip().startswith(row.code) else text
        section_id = str(_uuid.uuid4())
        sections.append(
            _SectionType(
                section_id=section_id,
                manual_id=manual_id,
                equipment_id=equipment_id,
                section_type="table",
                heading_path=("Fault Codes", row.code),
                page_start=row.page,
                page_end=row.page,
                text=full_text,
                error_codes=(row.code,),
            )
        )
        chunks.append(
            _ChunkType(
                chunk_id=str(_uuid.uuid4()),
                parent_section_id=section_id,
                manual_id=manual_id,
                equipment_id=equipment_id,
                section_type="table",
                heading_path=("Fault Codes", row.code),
                page=row.page,
                chunk_index=0,
                chunk_text=full_text,
                source_file=source_filename,
                error_codes=(row.code,),
            )
        )
    return sections, chunks


def _sanitize_section(section):
    return replace(
        section,
        text=_strip_nul(section.text),
        heading_path=_strip_nul(section.heading_path),
        error_codes=_strip_nul(section.error_codes),
    )


def _sanitize_chunk(chunk):
    return replace(
        chunk,
        chunk_text=_strip_nul(chunk.chunk_text),
        heading_path=_strip_nul(chunk.heading_path),
        source_file=_strip_nul(chunk.source_file),
    )


def _sanitize_chunk_v1(chunk):
    """v1 Chunk has no heading_path/error_codes — keep narrower."""
    return replace(
        chunk,
        chunk_text=_strip_nul(chunk.chunk_text),
        source_file=_strip_nul(chunk.source_file),
    )

logger = logging.getLogger(__name__)

Stage = Literal["parsing", "chunking", "embedding", "indexing", "done"]
ProgressCb = Callable[[Stage, float], None]


@dataclass(frozen=True)
class IngestResult:
    manual_id: str
    equipment_id: str
    source_filename: str
    chunks_inserted: int
    elapsed_s: float
    strategy: ChunkingStrategy = "v1"
    sections_inserted: int = 0  # 0 for v1 (no parent table)


def ingest_pdf(
    source: str | Path | bytes,
    *,
    manual_id: str,
    equipment_id: str,
    source_filename: str | None = None,
    store: VectorStore | None = None,
    strategy: ChunkingStrategy | None = None,
    progress_cb: ProgressCb | None = None,
) -> IngestResult:
    """Chunk + embed + persist a single PDF.

    `source` accepts either a filesystem path (str/Path) or the raw
    bytes of a PDF (e.g. from an HTTP multipart upload). When passing
    bytes, set `source_filename` so the stored chunk metadata records
    a meaningful filename.

    `strategy` selects the chunking pipeline. Defaults to settings.chunking_strategy.
      - 'v1': fixed-size character chunks → manual_chunks
      - 'v2': structure-aware sections + child chunks → manual_sections + manual_chunks_v2

    `progress_cb(stage, fraction)` is invoked at stage boundaries.
    """
    start = time.perf_counter()
    store = store or VectorStore()
    strategy = strategy or get_settings().chunking_strategy

    pdf_path, cleanup = _resolve_source(source, manual_id=manual_id)
    resolved_filename = source_filename or pdf_path.name

    try:
        if strategy == "v2":
            return _ingest_v2(
                pdf_path,
                manual_id=manual_id,
                equipment_id=equipment_id,
                resolved_filename=resolved_filename,
                store=store,
                progress_cb=progress_cb,
                start=start,
            )
        return _ingest_v1(
            pdf_path,
            manual_id=manual_id,
            equipment_id=equipment_id,
            resolved_filename=resolved_filename,
            source_filename=source_filename,
            store=store,
            progress_cb=progress_cb,
            start=start,
        )
    finally:
        cleanup()


def _ingest_v1(
    pdf_path: Path,
    *,
    manual_id: str,
    equipment_id: str,
    resolved_filename: str,
    source_filename: str | None,
    store: VectorStore,
    progress_cb: ProgressCb | None,
    start: float,
) -> IngestResult:
    _emit(progress_cb, "parsing", 0.0)
    _emit(progress_cb, "chunking", 0.1)
    chunks = chunk_pdf(pdf_path, manual_id=manual_id, equipment_id=equipment_id)
    if not chunks:
        logger.warning("no chunks produced", extra={"file": resolved_filename})
        return IngestResult(
            manual_id=manual_id,
            equipment_id=equipment_id,
            source_filename=resolved_filename,
            chunks_inserted=0,
            elapsed_s=time.perf_counter() - start,
            strategy="v1",
        )
    if source_filename:
        chunks = [replace(c, source_file=source_filename) for c in chunks]
    chunks = [_sanitize_chunk_v1(c) for c in chunks]

    _emit(progress_cb, "embedding", 0.3)
    pairs = embed_chunks(chunks)
    _emit(progress_cb, "indexing", 0.9)
    inserted = store.insert_chunks(pairs)
    _emit(progress_cb, "done", 1.0)

    elapsed = time.perf_counter() - start
    logger.info(
        "v1 ingest complete",
        extra={"manual_id": manual_id, "chunks_inserted": inserted, "elapsed_s": round(elapsed, 2)},
    )
    return IngestResult(
        manual_id=manual_id,
        equipment_id=equipment_id,
        source_filename=resolved_filename,
        chunks_inserted=inserted,
        elapsed_s=elapsed,
        strategy="v1",
    )


def _ingest_v2(
    pdf_path: Path,
    *,
    manual_id: str,
    equipment_id: str,
    resolved_filename: str,
    store: VectorStore,
    progress_cb: ProgressCb | None,
    start: float,
) -> IngestResult:
    settings = get_settings()
    _emit(progress_cb, "parsing", 0.0)
    _emit(progress_cb, "chunking", 0.1)
    result = chunk_pdf_structured(
        pdf_path,
        manual_id=manual_id,
        equipment_id=equipment_id,
        child_size=settings.v2_child_size,
        child_overlap=settings.v2_child_overlap,
    )
    # Override source_file on every child chunk so the recorded filename
    # is the caller-supplied one (matters for bytes uploads — temp file
    # name leaks otherwise).
    chunks = [replace(c, source_file=resolved_filename) for c in result.chunks]

    if not result.sections:
        logger.warning("no sections produced", extra={"file": resolved_filename})
        return IngestResult(
            manual_id=manual_id,
            equipment_id=equipment_id,
            source_filename=resolved_filename,
            chunks_inserted=0,
            sections_inserted=0,
            elapsed_s=time.perf_counter() - start,
            strategy="v2",
        )

    # LLM-driven fault-code pattern detection (per-manual whitelist).
    # Failures (no TOC fault list, LLM unreachable, validation reject) are
    # logged and we keep the chunking_v2 regex-derived error_codes.
    sections = list(result.sections)
    pattern_cache = pdf_path.parent / ".fault_patterns"
    try:
        pattern = detect_fault_pattern(
            pdf_path, manual_id, cache_dir=pattern_cache
        )
    except Exception as exc:  # noqa: BLE001 — never let LLM kill ingest
        logger.warning(
            "fault_pattern_detector raised — falling back to chunking regex",
            extra={"manual_id": manual_id, "error": str(exc)},
        )
        pattern = None

    if pattern and pattern.whitelist:
        rebuilt = []
        wl_size = len(pattern.whitelist)
        # When the detector has produced a whitelist, REPLACE every section's
        # error_codes with the whitelist intersection — never fall back to
        # the chunking_v2 regex result for that manual. The regex picks up
        # cross-vendor false positives (e.g. Mitsubishi sections tagged with
        # ABB-style 4-digit numbers from copyright pages), and once we have
        # a vetted vendor-specific whitelist that noise should not survive.
        for section in sections:
            new_codes = extract_codes_with_pattern(section.text, pattern)
            rebuilt.append(replace(section, error_codes=new_codes))
        sections = rebuilt
        logger.info(
            "applied LLM fault-pattern whitelist (replaced regex codes)",
            extra={"manual_id": manual_id, "whitelist_size": wl_size},
        )

    # Add table-row sections from the fault detector. Each row becomes a
    # standalone Section (and matching Chunk) so retrieval can match the
    # code token directly inside the same chunk that contains the row's
    # description text. Without this, vendors that put codes only in a
    # table cell (Schneider, Yaskawa) leave their fault description text
    # in chunks that don't contain the code → BM25 can't bridge them.
    if pattern and pattern.rows:
        extra_sections, extra_chunks = _build_table_row_sections(
            pattern, manual_id=manual_id, equipment_id=equipment_id,
            source_filename=resolved_filename,
        )
        if extra_sections:
            sections = list(sections) + extra_sections
            chunks = list(chunks) + extra_chunks
            logger.info(
                "added fault-table row sections",
                extra={"manual_id": manual_id, "rows": len(extra_sections)},
            )

    # NUL byte sanitisation — Postgres text fields reject \x00 (ATV320 case).
    sections = [_sanitize_section(s) for s in sections]
    chunks = [_sanitize_chunk(c) for c in chunks]

    # Sections must be inserted before chunks (FK constraint).
    sections_inserted = store.insert_sections(sections)

    _emit(progress_cb, "embedding", 0.3)
    pairs = embed_chunks_v2(chunks)
    _emit(progress_cb, "indexing", 0.9)
    chunks_inserted = store.insert_chunks_v2(pairs)
    _emit(progress_cb, "done", 1.0)

    elapsed = time.perf_counter() - start
    logger.info(
        "v2 ingest complete",
        extra={
            "manual_id": manual_id,
            "sections_inserted": sections_inserted,
            "chunks_inserted": chunks_inserted,
            "elapsed_s": round(elapsed, 2),
        },
    )
    return IngestResult(
        manual_id=manual_id,
        equipment_id=equipment_id,
        source_filename=resolved_filename,
        chunks_inserted=chunks_inserted,
        sections_inserted=sections_inserted,
        elapsed_s=elapsed,
        strategy="v2",
    )


def _resolve_source(
    source: str | Path | bytes,
    *,
    manual_id: str,
) -> tuple[Path, Callable[[], None]]:
    """Normalize the source argument to (path, cleanup_fn).

    Path inputs return a no-op cleanup; bytes inputs return a deleter
    for the temp file that holds the upload.
    """
    if isinstance(source, (str, Path)):
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(path)
        return path, lambda: None

    if isinstance(source, (bytes, bytearray, memoryview)):
        data = bytes(source)
        if not data:
            raise ValueError("empty PDF bytes")
        # delete=False so we can close before fitz reopens, then rm in cleanup.
        tmp = tempfile.NamedTemporaryFile(
            prefix=f"ingest_{manual_id}_", suffix=".pdf", delete=False
        )
        try:
            tmp.write(data)
        finally:
            tmp.close()
        tmp_path = Path(tmp.name)

        def cleanup() -> None:
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                logger.warning("failed to remove temp PDF", extra={"path": str(tmp_path)})

        return tmp_path, cleanup

    raise TypeError(f"unsupported source type: {type(source).__name__}")


def _emit(cb: ProgressCb | None, stage: Stage, fraction: float) -> None:
    if cb is None:
        return
    try:
        cb(stage, fraction)
    except Exception:
        logger.exception("progress_cb raised; ignoring")
