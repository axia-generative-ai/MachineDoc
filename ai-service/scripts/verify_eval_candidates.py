"""Run hybrid retriever over candidate eval set and emit a review markdown.

Output:
  - tests/eval/test_set_v2.review.md  (human-readable, ✓/✗ flags)
  - prints summary
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from app.pipelines.retrieval_v2 import (
    BM25Searcher,
    HybridRetriever,
    PreFilter,
    Reranker,
    VectorSearcher,
)

CAND = Path(__file__).resolve().parents[1] / "tests" / "eval" / "test_set_v2.candidates.json"
OUT = Path(__file__).resolve().parents[1] / "tests" / "eval" / "test_set_v2.review.md"


def page_overlap(expected: list[int], hit_page: int, slack: int = 5) -> bool:
    """A retrieval hit is considered correct if the page is within `slack`
    pages of the expected range. Vendor manuals often list a code in a
    table on one page (the "expected" first occurrence) and describe its
    cause/remedy on a nearby page within the same section — the user gets
    the answer either way.
    """
    if not expected:
        return False
    lo, hi = min(expected), max(expected)
    return (lo - slack) <= hit_page <= (hi + slack)


def main() -> None:
    cases = json.loads(CAND.read_text(encoding="utf-8"))
    pf = PreFilter.from_store()
    hr = HybridRetriever(
        pre_filter=pf,
        bm25=BM25Searcher(known_codes=pf.known_codes),
        vector=VectorSearcher(),
        reranker=Reranker(),
        candidate_k=20,
        final_k=3,
    )
    hr.retrieve("warmup")  # load reranker into GPU

    lines: list[str] = []
    lines.append("# v2 candidate eval review\n")
    lines.append(f"Cases: {len(cases)}  |  Top-3 manual+page check below\n")

    top1_pass = 0
    top3_pass = 0
    rows_summary: list[tuple[str, str, str, int]] = []

    for c in cases:
        t0 = time.perf_counter()
        hits = hr.retrieve(c["natural_language_query"])
        ms = (time.perf_counter() - t0) * 1000

        # A hit counts as correct if it is in the right manual AND either
        # (a) within the expected page range (with slack), OR
        # (b) the chunk text contains the queried error code (different
        #     occurrence of the same code is still useful to the user).
        code = (c.get("error_code") or "").strip()
        rank_hit = None
        for i, h in enumerate(hits, start=1):
            if h.manual_id != c["expected_manual_id"]:
                continue
            page_ok = page_overlap(c["expected_pages"], h.page)
            code_ok = bool(code) and code in (h.chunk_text or "")
            if page_ok or code_ok:
                rank_hit = i
                break
        flag = "✓" if rank_hit else "✗"
        if rank_hit == 1:
            top1_pass += 1
        if rank_hit:
            top3_pass += 1

        lines.append(f"## {flag} `{c['id']}` — {c['query_type']}  ({ms:.0f}ms)")
        lines.append(f"- **query**: {c['natural_language_query']}")
        lines.append(
            f"- **expected**: `{c['expected_manual_id']}` p{c['expected_pages'][0]}-{c['expected_pages'][1]} "
            f"({c['section_type']}) — {(' / '.join(c['heading_path'][:2]))[:120]}"
        )
        lines.append(f"- **snippet**: `{c['snippet'][:160]}`")
        lines.append("- **top-3**:")
        for i, h in enumerate(hits, 1):
            mark = "  ✓" if i == rank_hit else ""
            lines.append(
                f"    {i}. [{h.source} {h.score:.3f}] {h.manual_id} p{h.page} — "
                f"{(' / '.join(h.heading_path[:2]))[:100]}{mark}"
            )
        lines.append("")
        rows_summary.append((c["id"], c["expected_manual_id"], c["natural_language_query"], rank_hit or 0))

    lines.insert(2, f"\n**Top-1**: {top1_pass}/{len(cases)} ({top1_pass/len(cases)*100:.0f}%)  |  **Top-3**: {top3_pass}/{len(cases)} ({top3_pass/len(cases)*100:.0f}%)\n")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT}")
    print(f"Top-1 {top1_pass}/{len(cases)}  Top-3 {top3_pass}/{len(cases)}")
    for cid, mid, q, rank in rows_summary:
        flag = f"#{rank}" if rank else "MISS"
        print(f"  {cid} {flag:6s} {mid:40s} {q[:60]}")


if __name__ == "__main__":
    main()
