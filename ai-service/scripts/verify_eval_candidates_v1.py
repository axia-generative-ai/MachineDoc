"""Run v1 retrieval (similarity_search only, no BM25 / no reranker) over the
SAME multi-vendor eval set used for v2 (`test_set_v2.candidates.json`).

Apples-to-apples A/B with verify_eval_candidates.py:
  - Same corpus (8 real manuals).
  - Same eval set (25 cases).
  - Same correctness rule (page_overlap with slack OR code-in-chunk).
  - Difference is only chunking_v1 + vector-only retrieval.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from app.core.embeddings import get_embeddings
from app.core.vectorstore import VectorStore

CAND = Path(__file__).resolve().parents[1] / "tests" / "eval" / "test_set_v2.candidates.json"
OUT = Path(__file__).resolve().parents[1] / "tests" / "eval" / "test_set_v2.review.v1.md"


def page_overlap(expected: list[int], hit_page: int, slack: int = 5) -> bool:
    if not expected:
        return False
    lo, hi = min(expected), max(expected)
    return (lo - slack) <= hit_page <= (hi + slack)


def main() -> None:
    cases = json.loads(CAND.read_text(encoding="utf-8"))
    store = VectorStore()
    embedder = get_embeddings()
    final_k = 3

    lines: list[str] = ["# v1 retrieval review (same eval set as v2)\n"]
    top1 = top3 = 0
    summary: list[tuple[str, str, str, int]] = []

    for c in cases:
        t0 = time.perf_counter()
        qvec = embedder.embed_query(c["natural_language_query"])
        hits = store.similarity_search(qvec, k=final_k)
        ms = (time.perf_counter() - t0) * 1000

        code = (c.get("error_code") or "").strip()
        rank = None
        for i, h in enumerate(hits, start=1):
            if h.manual_id != c["expected_manual_id"]:
                continue
            page_ok = page_overlap(c["expected_pages"], h.page)
            code_ok = bool(code) and code in (h.chunk_text or "")
            if page_ok or code_ok:
                rank = i
                break
        flag = "✓" if rank else "✗"
        if rank == 1:
            top1 += 1
        if rank:
            top3 += 1

        lines.append(f"## {flag} `{c['id']}` ({ms:.0f}ms)")
        lines.append(f"- query: {c['natural_language_query']}")
        lines.append(
            f"- expected: `{c['expected_manual_id']}` p{c['expected_pages'][0]}-{c['expected_pages'][1]}"
        )
        lines.append("- top-3:")
        for i, h in enumerate(hits, 1):
            mark = "  ✓" if i == rank else ""
            lines.append(
                f"    {i}. [vector dist={h.distance:.3f}] {h.manual_id} p{h.page}{mark}"
            )
        lines.append("")
        summary.append((c["id"], c["expected_manual_id"], c["natural_language_query"], rank or 0))

    lines.insert(1, f"\n**Top-1**: {top1}/{len(cases)} ({top1/len(cases)*100:.0f}%)  |  "
                    f"**Top-3**: {top3}/{len(cases)} ({top3/len(cases)*100:.0f}%)\n")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT}")
    print(f"Top-1 {top1}/{len(cases)}  Top-3 {top3}/{len(cases)}")
    for cid, mid, q, r in summary:
        flag = f"#{r}" if r else "MISS"
        print(f"  {cid} {flag:6s} {mid:40s} {q[:60]}")


if __name__ == "__main__":
    main()
