"""Stage-by-stage diagnostics for v2 eval miss cases.

For each miss, prints:
  - PreFilter resolution (codes detected, equipment filter)
  - BM25 top-20 (with rank of gold chunk if present)
  - Vector top-20 (with rank of gold chunk if present)
  - Post-RRF top-20
  - Post-rerank top-3
  - Whether the gold section was indexed at all

Run:  uv run python tests/eval/debug_misses.py
"""

from __future__ import annotations

import io
import json
import logging
import sys
from pathlib import Path

# Windows console is cp949 by default; force UTF-8 so em-dashes etc. print.
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from app.core.vectorstore import VectorStore
from app.pipelines.retrieval_v2 import (
    BM25Searcher,
    HybridRetriever,
    PreFilter,
    Reranker,
    VectorSearcher,
    reciprocal_rank_fusion,
)

ROOT = Path(__file__).resolve().parents[2]
TEST_SET = ROOT / "tests" / "eval" / "test_set_v2.json"

# Latest miss IDs from v2_20260508-175420.json
MISS_IDS = {"v2_002", "v2_019", "v2_020", "v2_022", "v2_023", "v2_025"}

logging.basicConfig(level="WARNING", format="%(levelname)s %(message)s")


def _rank_of_gold(hits, expected_section_id, expected_pages, expected_manual):
    """Return (rank_by_section, rank_by_page) — 1-based; None if absent."""
    section_rank = None
    page_rank = None
    for i, h in enumerate(hits, start=1):
        if h.manual_id != expected_manual:
            continue
        if section_rank is None and h.parent_section_id == expected_section_id:
            section_rank = i
        if page_rank is None and h.page in set(expected_pages):
            page_rank = i
    return section_rank, page_rank


def main() -> None:
    cases = {c["id"]: c for c in json.loads(TEST_SET.read_text(encoding="utf-8"))}
    store = VectorStore()
    pre = PreFilter.from_store(store)
    bm25 = BM25Searcher(store=store, known_codes=pre.known_codes)
    vec = VectorSearcher(store=store)
    reranker = Reranker()

    # Warm reranker on a throwaway call so timing prints are clean.
    HybridRetriever(pre, bm25, vec, reranker).retrieve("warmup")

    for cid in sorted(MISS_IDS):
        c = cases[cid]
        q = c["natural_language_query"]
        exp_manual = c["expected_manual_id"]
        exp_section = c["expected_section_id"]
        exp_pages = c["expected_pages"]

        print(f"\n========== {cid} | {c['error_code']} ==========")
        print(f"query: {q}")
        print(f"expected: {exp_manual} / section={exp_section[:8]}.. / pages={exp_pages}")

        # --- gold availability check ---
        with store._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*) FROM manual_chunks_v2
                 WHERE manual_id=%s AND parent_section_id=%s
                """,
                (exp_manual, exp_section),
            )
            chunk_count = cur.fetchone()[0]
            cur.execute(
                """
                SELECT heading_path, page_start, page_end, error_codes
                  FROM manual_sections
                 WHERE section_id=%s
                """,
                (exp_section,),
            )
            row = cur.fetchone()
        print(f"gold chunks indexed: {chunk_count}")
        if row:
            hp, ps, pe, codes = row
            print(f"gold section: heading={hp} pages={ps}-{pe} codes={codes}")

        # --- PreFilter ---
        codes = pre.known_codes_in(q)
        eq = pre.resolve(q)
        print(f"PreFilter: codes_detected={list(codes)} equipment_filter={eq}")

        # --- BM25 ---
        bm25_hits = bm25.search(q, equipment_ids=eq, k=20)
        sr, pr = _rank_of_gold(bm25_hits, exp_section, exp_pages, exp_manual)
        print(f"BM25 top-20: gold section_rank={sr} page_rank={pr} | scores[0..2]="
              f"{[round(h.score,3) for h in bm25_hits[:3]]}")
        for i, h in enumerate(bm25_hits[:5], 1):
            mark = " <-- GOLD-SECTION" if h.parent_section_id == exp_section else (
                " <-- gold-page" if h.page in set(exp_pages) and h.manual_id == exp_manual else ""
            )
            print(f"  bm25 #{i} {h.manual_id} p{h.page} score={h.score:.3f}{mark}")

        # --- Vector ---
        vec_hits = vec.search(q, equipment_ids=eq, k=20)
        sr, pr = _rank_of_gold(vec_hits, exp_section, exp_pages, exp_manual)
        print(f"Vector top-20: gold section_rank={sr} page_rank={pr} | sims[0..2]="
              f"{[round(h.score,3) for h in vec_hits[:3]]}")
        for i, h in enumerate(vec_hits[:5], 1):
            mark = " <-- GOLD-SECTION" if h.parent_section_id == exp_section else (
                " <-- gold-page" if h.page in set(exp_pages) and h.manual_id == exp_manual else ""
            )
            print(f"  vec  #{i} {h.manual_id} p{h.page} sim={h.score:.3f}{mark}")

        # --- RRF ---
        fused = reciprocal_rank_fusion([bm25_hits, vec_hits], k=20)
        sr, pr = _rank_of_gold(fused, exp_section, exp_pages, exp_manual)
        print(f"RRF top-20:    gold section_rank={sr} page_rank={pr}")

        # --- Rerank ---
        reranked = reranker.rerank(q, fused, top_k=3)
        sr, pr = _rank_of_gold(reranked, exp_section, exp_pages, exp_manual)
        print(f"Rerank top-3:  gold section_rank={sr} page_rank={pr}")
        for i, h in enumerate(reranked, 1):
            mark = " <-- GOLD-SECTION" if h.parent_section_id == exp_section else (
                " <-- gold-page" if h.page in set(exp_pages) and h.manual_id == exp_manual else ""
            )
            print(f"  rr   #{i} {h.manual_id} p{h.page} score={h.score:.3f}{mark}")


if __name__ == "__main__":
    main()
