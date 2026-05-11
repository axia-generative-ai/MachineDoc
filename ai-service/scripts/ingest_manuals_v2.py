"""Ingest manuals/*.pdf into the v2 vectorstore (manual_sections + manual_chunks_v2).

Reads manuals/manual_index.json (Phase 6 real manuals) and runs the
structure-aware chunking pipeline against each PDF. Truncates v2 tables
first for an idempotent reload — v1 tables (manual_chunks) are NOT touched.

Run (after init_db.py + Ollama daemon up):
    uv run python scripts/ingest_manuals_v2.py
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path

from app.core.vectorstore import VectorStore
from app.services.ingest_service import ingest_pdf

ROOT = Path(__file__).resolve().parents[1]
MANUAL_DIR = ROOT / "manuals"
INDEX = MANUAL_DIR / "manual_index.json"

logging.basicConfig(level="INFO", format="%(levelname)s %(message)s")
log = logging.getLogger("ingest_v2")


def main() -> None:
    if not INDEX.exists():
        raise SystemExit(f"missing {INDEX}")
    records = json.loads(INDEX.read_text(encoding="utf-8"))
    if not records:
        raise SystemExit("manual_index.json is empty")

    store = VectorStore()
    log.info("truncating v2 tables (CASCADE)")
    store.truncate_v2()

    overall_start = time.perf_counter()
    total_sections = 0
    total_chunks = 0
    for rec in records:
        pdf = MANUAL_DIR / rec["manual_filename"]
        if not pdf.exists():
            log.warning("missing %s — skipping", pdf)
            continue
        log.info(
            "ingesting %s (manual=%s equipment=%s pages=%s)",
            pdf.name, rec["manual_id"], rec["equipment_id"], rec.get("page_count", "?"),
        )
        result = ingest_pdf(
            pdf,
            manual_id=rec["manual_id"],
            equipment_id=rec["equipment_id"],
            store=store,
            strategy="v2",
        )
        log.info(
            "  -> sections=%d chunks=%d in %.1fs",
            result.sections_inserted, result.chunks_inserted, result.elapsed_s,
        )
        total_sections += result.sections_inserted
        total_chunks += result.chunks_inserted

    elapsed = time.perf_counter() - overall_start
    sections, chunks = store.count_v2()
    log.info(
        "v2 ingest complete: sections=%d chunks=%d in %.1fs (db sees sections=%d chunks=%d)",
        total_sections, total_chunks, elapsed, sections, chunks,
    )


if __name__ == "__main__":
    main()
