"""KPI evaluation runner for the v2 hybrid retrieval pipeline.

Scores Top-K against `test_set_v2.json`. A case is correct when at least
one retrieved hit matches the expected manual AND either:

  - hit.parent_section_id == expected_section_id, OR
  - hit.page is in expected_pages

The section_id path is the strict win; the page fallback covers cases
where structure-aware chunking attached the answer to a sibling section
on the same page (still a usable retrieval).

CLI:
    uv run python tests/eval/run_eval_v2.py
    uv run python tests/eval/run_eval_v2.py --top-k 3 --threshold 0.8
    uv run python tests/eval/run_eval_v2.py --output tests/eval/results/run.json
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from app.core.vectorstore import VectorStore
from app.pipelines.retrieval_v2 import (
    BM25Searcher,
    HybridRetriever,
    PreFilter,
    Reranker,
    VectorSearcher,
)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TEST_SET = ROOT / "tests" / "eval" / "test_set_v2.json"
DEFAULT_RESULTS_DIR = ROOT / "tests" / "eval" / "results"

log = logging.getLogger("run_eval_v2")
logging.basicConfig(level="INFO", format="%(levelname)s %(message)s")


@dataclass
class CaseResult:
    case_id: str
    query: str
    error_code: str
    expected_manual_id: str
    expected_section_id: str
    expected_pages: list[int]
    retrieved: list[dict]
    manual_match: bool
    section_match: bool
    page_match: bool
    correct: bool
    retrieval_ms: int


def _score(case: dict, retrieved: list[dict]) -> tuple[bool, bool, bool]:
    expected_manual = case["expected_manual_id"]
    expected_section = case.get("expected_section_id")
    expected_pages = set(case.get("expected_pages") or [])

    manual_match = any(r["manual_id"] == expected_manual for r in retrieved)
    section_match = bool(expected_section) and any(
        r["manual_id"] == expected_manual and r["parent_section_id"] == expected_section
        for r in retrieved
    )
    page_match = any(
        r["manual_id"] == expected_manual and r["page"] in expected_pages
        for r in retrieved
    )
    return manual_match, section_match, page_match


def run(
    test_set_path: Path,
    *,
    top_k: int,
    threshold: float,
    candidate_k: int,
) -> tuple[list[CaseResult], dict]:
    if not test_set_path.exists():
        log.error("test set not found: %s", test_set_path)
        sys.exit(2)
    cases = json.loads(test_set_path.read_text(encoding="utf-8"))

    log.info("building PreFilter from store...")
    store = VectorStore()
    pre_filter = PreFilter.from_store(store)
    log.info(
        "PreFilter ready (codes=%d, known=%d)",
        len(pre_filter.error_code_to_equipment),
        len(pre_filter.known_codes),
    )

    retriever = HybridRetriever(
        pre_filter=pre_filter,
        bm25=BM25Searcher(store=store, known_codes=pre_filter.known_codes),
        vector=VectorSearcher(store=store),
        reranker=Reranker(),
        candidate_k=candidate_k,
        final_k=top_k,
    )

    # Warmup: load reranker model + first embed/BM25 round-trip.
    log.info("warmup retrieval (loads reranker model)...")
    t_warm = time.perf_counter()
    retriever.retrieve("warmup query")
    log.info("warmup done in %.1fs", time.perf_counter() - t_warm)

    results: list[CaseResult] = []
    correct_count = 0
    total_retrieval_ms = 0

    for case in cases:
        t0 = time.perf_counter()
        hits = retriever.retrieve(case["natural_language_query"], final_k=top_k)
        rt_ms = int((time.perf_counter() - t0) * 1000)

        retrieved = [
            {
                "manual_id": h.manual_id,
                "parent_section_id": h.parent_section_id,
                "page": h.page,
                "score": round(h.score, 4),
                "source": h.source,
            }
            for h in hits
        ]
        manual_match, section_match, page_match = _score(case, retrieved)
        correct = manual_match and (section_match or page_match)
        if correct:
            correct_count += 1

        results.append(
            CaseResult(
                case_id=case["id"],
                query=case["natural_language_query"],
                error_code=case.get("error_code", ""),
                expected_manual_id=case["expected_manual_id"],
                expected_section_id=case.get("expected_section_id", ""),
                expected_pages=case.get("expected_pages") or [],
                retrieved=retrieved,
                manual_match=manual_match,
                section_match=section_match,
                page_match=page_match,
                correct=correct,
                retrieval_ms=rt_ms,
            )
        )
        total_retrieval_ms += rt_ms

        if correct:
            tag = "OK  "
            detail = "section" if section_match else "page"
        elif manual_match:
            tag = "MISS"
            detail = "manual-only"
        else:
            tag = "MISS"
            detail = "no-manual"
        log.info(
            "%s %s [%s] %s | %dms | top=%s",
            tag,
            case["id"],
            case.get("error_code", ""),
            detail,
            rt_ms,
            [(r["manual_id"], r["page"]) for r in retrieved],
        )

    n = len(cases)
    accuracy = correct_count / n if n else 0.0
    summary = {
        "test_set": str(test_set_path),
        "ran_at": datetime.now(timezone.utc).isoformat(),
        "total_cases": n,
        "correct": correct_count,
        "accuracy": round(accuracy, 4),
        "kpi_threshold": threshold,
        "kpi_pass": accuracy >= threshold,
        "top_k": top_k,
        "candidate_k": candidate_k,
        "avg_retrieval_ms": round(total_retrieval_ms / n, 1) if n else 0.0,
    }
    return results, summary


def write_reports(results: list[CaseResult], summary: dict, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(
            {"summary": summary, "cases": [asdict(r) for r in results]},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    csv_path = out_path.with_suffix(".csv")
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "case_id", "error_code", "expected_manual_id", "expected_section_id",
            "expected_pages", "retrieved", "manual_match", "section_match",
            "page_match", "correct", "retrieval_ms",
        ])
        for r in results:
            w.writerow([
                r.case_id, r.error_code, r.expected_manual_id, r.expected_section_id,
                "|".join(map(str, r.expected_pages)),
                "|".join(f"{x['manual_id']}:p{x['page']}" for x in r.retrieved),
                int(r.manual_match), int(r.section_match), int(r.page_match),
                int(r.correct), r.retrieval_ms,
            ])
    log.info("wrote %s", out_path.relative_to(ROOT))
    log.info("wrote %s", csv_path.relative_to(ROOT))


def main() -> None:
    ap = argparse.ArgumentParser(description="MachineDoc v2 RAG eval runner")
    ap.add_argument("--test-set", type=Path, default=DEFAULT_TEST_SET)
    ap.add_argument("--output", type=Path, default=None)
    ap.add_argument("--top-k", type=int, default=3)
    ap.add_argument("--candidate-k", type=int, default=20)
    ap.add_argument("--threshold", type=float, default=0.8)
    args = ap.parse_args()

    if args.output is None:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        args.output = DEFAULT_RESULTS_DIR / f"v2_{ts}.json"

    results, summary = run(
        args.test_set,
        top_k=args.top_k,
        threshold=args.threshold,
        candidate_k=args.candidate_k,
    )
    write_reports(results, summary, args.output)

    log.info(
        "accuracy = %.1f%% (%d/%d), KPI %s @ %.0f%% (avg retrieval %.0fms)",
        summary["accuracy"] * 100,
        summary["correct"],
        summary["total_cases"],
        "PASS" if summary["kpi_pass"] else "FAIL",
        summary["kpi_threshold"] * 100,
        summary["avg_retrieval_ms"],
    )

    sys.exit(0 if summary["kpi_pass"] else 1)


if __name__ == "__main__":
    main()
