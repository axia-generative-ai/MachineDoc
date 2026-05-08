"""Incrementally ingest the 3 newly added manuals (Yaskawa GA700, Rockwell PowerFlex 520,
Schneider ATV320) into the v2 vectorstore without truncating existing data.

Skips any manual_id that already has rows in manual_sections.
"""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path

import psycopg

from app.config import get_settings
from app.core.vectorstore import VectorStore, _normalise_dsn
from app.services.ingest_service import ingest_pdf

ROOT = Path(__file__).resolve().parents[1]
MANUAL_DIR = ROOT / "manuals"
INDEX = MANUAL_DIR / "manual_index.json"
TARGET_MANUAL_IDS = {
    "yaskawa_ga700_technical",
    "rockwell_powerflex520_user",
    "schneider_atv320_programming",
}

logging.basicConfig(level="INFO", format="%(levelname)s %(message)s")
log = logging.getLogger("ingest_added")


def _existing_manual_ids() -> set[str]:
    dsn = _normalise_dsn(get_settings().database_url)
    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute("SELECT DISTINCT manual_id FROM manual_sections")
        return {r[0] for r in cur.fetchall()}


def main() -> None:
    records = json.loads(INDEX.read_text(encoding="utf-8"))
    targets = [r for r in records if r["manual_id"] in TARGET_MANUAL_IDS]
    if not targets:
        raise SystemExit("No target manuals found in manual_index.json")

    existing = _existing_manual_ids()
    store = VectorStore()
    overall_start = time.perf_counter()

    for rec in targets:
        if rec["manual_id"] in existing:
            log.info("skipping %s (already present)", rec["manual_id"])
            continue
        pdf = MANUAL_DIR / rec["manual_filename"]
        if not pdf.exists():
            log.warning("missing %s — skipping", pdf)
            continue
        log.info(
            "ingesting %s (manual=%s pages=%s)",
            pdf.name, rec["manual_id"], rec.get("page_count", "?"),
        )
        t0 = time.perf_counter()
        result = ingest_pdf(
            pdf,
            manual_id=rec["manual_id"],
            equipment_id=rec["equipment_id"],
            store=store,
            strategy="v2",
        )
        log.info(
            "  -> sections=%d chunks=%d in %.1fs",
            result.sections_inserted, result.chunks_inserted,
            time.perf_counter() - t0,
        )

    sections, chunks = store.count_v2()
    log.info(
        "done in %.1fs total — db now has sections=%d chunks=%d",
        time.perf_counter() - overall_start, sections, chunks,
    )


if __name__ == "__main__":
    main()
