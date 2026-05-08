"""Multi-manual evaluation set generator (LLM-detector-aware).

Design (locked 2026-05-07, revised after fault_pattern_detector)
---------------------------------------------------------------
- Uses ONLY error-code lookup cases (NL heading queries proved noisy).
- Trusts `manual_sections.error_codes` — that column is now populated by
  the LLM-driven `fault_pattern_detector` whitelist (Yaskawa, Rockwell,
  Schneider, ...) plus `chunking_v2._extract_error_codes` for manuals
  that fall back to the regex path (ABB, Fanuc, LS, Mits, Sie).
- Per-manual canonical-entry detection is replaced by a single rule:
  pick the section with the LOWEST page_start that contains the code
  (the first occurrence is almost always the dedicated description in
  vendors that have a fault list; for the regex-fallback vendors it
  matches their existing semantics).
- Sampling is stratified across pages within each manual; cases are
  distributed proportionally across manuals by canonical pool size,
  with a minimum allocation per manual that has any codes.
- Query templates are vendor-flavoured to make distractor manuals
  meaningful rather than trivially separable by keyword.

Output: tests/eval/test_set_v2.candidates.json (still 25 cases by default).
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

from app.config import get_settings
from app.core.vectorstore import _normalise_dsn

OUT = Path(__file__).resolve().parents[1] / "tests" / "eval" / "test_set_v2.candidates.json"
SEED = 20260507
TOTAL = 25
MIN_PER_MANUAL = 1

random.seed(SEED)

# Vendor-flavoured templates. Picked at random per case so distractor
# manuals can't win on simple keyword overlap.
QUERY_TEMPLATES: dict[str, list[str]] = {
    "abb_irb_troubleshooting": [
        "What does ABB IRB error {code} mean?",
        "How do I fix ABB robot error {code}?",
        "ABB robot error {code}, what should I do?",
        "Troubleshooting steps for ABB error {code}",
    ],
    "fanuc_series0m_maintenance": [
        "What does Fanuc alarm {code} mean?",
        "Fanuc Series 0 alarm {code}, recommended action?",
        "How do I clear Fanuc CNC alarm {code}?",
        "Fanuc maintenance — alarm code {code}",
    ],
    "ls_s100_rapienet_user": [
        "What does LS S100 RAPIEnet parameter {code} configure?",
        "LS S100 inverter parameter {code} — function?",
        "Where is LS S100 parameter {code} described?",
    ],
    "mitsubishi_servo_amp_instruction": [
        "Mitsubishi servo amp alarm {code} — cause and remedy?",
        "What does Mitsubishi alarm {code} indicate?",
        "MR-J4 servo error {code}, troubleshooting?",
    ],
    "rockwell_powerflex520_user": [
        "PowerFlex 520 fault {code} — meaning?",
        "Rockwell PowerFlex parameter {code} description?",
        "Allen-Bradley drive code {code}, what to do?",
    ],
    "schneider_atv320_programming": [
        "Schneider ATV320 fault {code} — cause?",
        "Altivar 320 error {code}, recommended action?",
        "ATV320 detection code {code} explanation",
    ],
    "siemens_s7_diagnostics": [
        "Siemens S7 diagnostics — code {code} meaning?",
        "SIMATIC S7 error {code} description?",
    ],
    "yaskawa_ga700_technical": [
        "Yaskawa GA700 fault {code} — meaning?",
        "GA700 drive alarm {code}, what to do?",
        "Yaskawa drive code {code} troubleshooting",
    ],
}

GENERIC_TEMPLATE = "What does error code {code} mean?"


def _connect():
    return psycopg.connect(_normalise_dsn(get_settings().database_url), row_factory=dict_row)


def _fetch_rows_with_codes(cur, manual_id: str) -> list[dict]:
    cur.execute(
        """
        SELECT section_id, manual_id, equipment_id, page_start, page_end,
               heading_path, error_codes, section_type, section_text
        FROM manual_sections
        WHERE manual_id = %s
          AND error_codes IS NOT NULL
          AND array_length(error_codes, 1) > 0
        ORDER BY page_start, section_id
        """,
        (manual_id,),
    )
    return cur.fetchall()


def _canonical_by_code(rows: list[dict]) -> dict[str, dict]:
    """For each code in this manual, pick the row with the lowest page_start."""
    chosen: dict[str, dict] = {}
    for r in rows:
        for code in r["error_codes"] or []:
            current = chosen.get(code)
            if current is None or r["page_start"] < current["page_start"]:
                chosen[code] = r
    return chosen


def _stratified_sample(codes: list[str], k: int, page_of: dict[str, int]) -> list[str]:
    if k <= 0:
        return []
    if k >= len(codes):
        return list(codes)
    ordered = sorted(codes, key=lambda c: page_of[c])
    bucket_size = len(ordered) / k
    sampled: list[str] = []
    for i in range(k):
        lo = int(i * bucket_size)
        hi = int((i + 1) * bucket_size)
        bucket = ordered[lo:hi] or [ordered[lo]]
        sampled.append(random.choice(bucket))
    return sampled


def _allocate_shares(pool_sizes: dict[str, int], total: int) -> dict[str, int]:
    """Allocate `total` cases across manuals proportional to pool size,
    but reserving MIN_PER_MANUAL for every manual that has any codes.
    """
    eligible = {m: n for m, n in pool_sizes.items() if n > 0}
    if not eligible:
        return {}

    # First pass: reserve MIN_PER_MANUAL each
    reserved = {m: min(MIN_PER_MANUAL, n) for m, n in eligible.items()}
    used = sum(reserved.values())
    remaining = total - used
    if remaining <= 0:
        # Can't fit min for everyone — drop smallest pools
        items = sorted(eligible.items(), key=lambda kv: kv[1], reverse=True)
        out: dict[str, int] = {}
        for m, _ in items[:total]:
            out[m] = 1
        return out

    # Second pass: distribute remaining proportionally to (pool_size - 1)
    weights = {m: max(0, n - 1) for m, n in eligible.items()}
    weight_sum = sum(weights.values())
    if weight_sum == 0:
        return reserved
    extra = {
        m: math.floor(remaining * w / weight_sum) for m, w in weights.items()
    }
    short = remaining - sum(extra.values())
    # Hand out leftovers to manuals with the largest fractional remainders
    fracs = sorted(
        ((m, (remaining * weights[m] / weight_sum) - extra[m]) for m in eligible),
        key=lambda kv: -kv[1],
    )
    for m, _ in fracs[:short]:
        extra[m] += 1
    final: dict[str, int] = {}
    for m, base in reserved.items():
        final[m] = min(eligible[m], base + extra.get(m, 0))
    return final


def _make_case(case_id: str, code: str, row: dict) -> dict:
    templates = QUERY_TEMPLATES.get(row["manual_id"], [GENERIC_TEMPLATE])
    template = random.choice(templates)
    return {
        "id": case_id,
        "query_type": "error_code",
        "error_code": code,
        "natural_language_query": template.format(code=code),
        "expected_manual_id": row["manual_id"],
        "expected_section_id": str(row["section_id"]),
        "expected_pages": [row["page_start"], row["page_end"]],
        "heading_path": row["heading_path"],
        "section_type": row["section_type"],
        "snippet": (row["section_text"] or "")[:200],
    }


def main() -> None:
    canonical_per_manual: dict[str, dict[str, dict]] = {}
    with _connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT DISTINCT manual_id FROM manual_sections ORDER BY manual_id")
        manuals = [r["manual_id"] for r in cur.fetchall()]
        for mid in manuals:
            rows = _fetch_rows_with_codes(cur, mid)
            canonical_per_manual[mid] = _canonical_by_code(rows)

    pool_sizes = {m: len(c) for m, c in canonical_per_manual.items()}
    shares = _allocate_shares(pool_sizes, TOTAL)

    print("Pool sizes / allocated:")
    for m in sorted(pool_sizes.keys()):
        print(f"  {m:<42s}  pool={pool_sizes[m]:>5d}  picked={shares.get(m, 0)}")

    cases: list[dict] = []
    counter = 0
    for mid in sorted(shares.keys()):
        canonical = canonical_per_manual[mid]
        page_of = {c: r["page_start"] for c, r in canonical.items()}
        sampled = _stratified_sample(list(canonical.keys()), shares[mid], page_of)
        for code in sampled:
            counter += 1
            cases.append(_make_case(f"v2_{counter:03d}", code, canonical[code]))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(cases, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {len(cases)} cases to {OUT}")
    by_manual: dict[str, int] = {}
    for c in cases:
        by_manual[c["expected_manual_id"]] = by_manual.get(c["expected_manual_id"], 0) + 1
    print("Final distribution:")
    for k, v in sorted(by_manual.items()):
        print(f"  {k:<42s}  {v}")


if __name__ == "__main__":
    main()
