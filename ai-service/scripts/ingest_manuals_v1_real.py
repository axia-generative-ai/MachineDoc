"""Ingest the 8 real manuals (manuals/) using the v1 chunking pipeline.

Used for the AI-27 v1↔v2 A/B comparison: same corpus, same eval set, only
the chunking + retrieval pipeline differs. Truncates the v1 chunks table
first; v2 tables are NOT touched.
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
log = logging.getLogger("ingest_v1")


def main() -> None:
    records = json.loads(INDEX.read_text(encoding="utf-8"))
    if not records:
        raise SystemExit("empty manual_index.json")

    store = VectorStore()
    log.info("truncating v1 manual_chunks")
    store.truncate()

    overall_start = time.perf_counter()
    total = 0
    for rec in records:
        pdf = MANUAL_DIR / rec["manual_filename"]
        if not pdf.exists():
            log.warning("missing %s — skipping", pdf)
            continue
        log.info(
            "ingesting %s (manual=%s pages=%s)",
            pdf.name, rec["manual_id"], rec.get("page_count", "?"),
        )
        result = ingest_pdf(
            pdf,
            manual_id=rec["manual_id"],
            equipment_id=rec["equipment_id"],
            store=store,
            strategy="v1",
        )
        log.info("  -> chunks=%d in %.1fs", result.chunks_inserted, result.elapsed_s)
        total += result.chunks_inserted

    log.info(
        "v1 ingest done: chunks=%d in %.1fs (db sees %d)",
        total, time.perf_counter() - overall_start, store.count(),
    )


if __name__ == "__main__":
    main()
