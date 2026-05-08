"""Unit tests for the structure-aware retrieval skeleton.

Covers the two pieces that don't need a live PG:
- `PreFilter.resolve` — error-code-to-equipment routing
- `reciprocal_rank_fusion` — score math + dedup behavior
- `KoreanResponseRules.normalize` — guarantees required section headers

The DB-backed searchers (BM25Searcher, VectorSearcher) and the full
RagPipelineV2.build are intentionally NOT tested here; they raise
NotImplementedError until schema+wiring land.
"""

from __future__ import annotations

from app.pipelines.rag_v2 import KoreanResponseRules
from app.pipelines.retrieval_v2 import (
    Hit,
    PreFilter,
    reciprocal_rank_fusion,
)


def _hit(chunk_id: str, *, manual="M1", equipment="EQ-001") -> Hit:
    return Hit(
        chunk_id=chunk_id,
        parent_section_id=f"parent-{chunk_id}",
        manual_id=manual,
        equipment_id=equipment,
        section_type="narrative",
        heading_path=("root",),
        page=1,
        chunk_text=f"text-{chunk_id}",
        score=0.0,
        source="bm25",
    )


# ---------- PreFilter ----------


def test_prefilter_explicit_equipment_wins() -> None:
    pf = PreFilter(error_code_to_equipment={"E-204": "EQ-002"})
    assert pf.resolve("E-204 발생", equipment_id="EQ-009") == ["EQ-009"]


def test_prefilter_routes_via_error_code() -> None:
    pf = PreFilter(error_code_to_equipment={"E-204": "EQ-002", "E-101": "EQ-001"})
    assert pf.resolve("E-204 / E-101 같이") == ["EQ-001", "EQ-002"]


def test_prefilter_returns_none_when_no_match() -> None:
    pf = PreFilter(error_code_to_equipment={"E-204": "EQ-002"})
    assert pf.resolve("베어링 윤활 부족") is None


# ---------- RRF ----------


def test_rrf_empty_runs() -> None:
    assert reciprocal_rank_fusion([], k=5) == []


def test_rrf_dedups_and_boosts_shared_hits() -> None:
    # "a" appears in both runs at the top → should win over "b"/"c"
    bm25 = [_hit("a"), _hit("b"), _hit("c")]
    vec = [_hit("a"), _hit("d")]

    fused = reciprocal_rank_fusion([bm25, vec], k=3)
    ids = [h.chunk_id for h in fused]
    assert ids[0] == "a"
    assert set(ids) == {"a", "b", "d"}  # c drops out at k=3


def test_rrf_marks_source_as_rrf() -> None:
    fused = reciprocal_rank_fusion([[_hit("a")]], k=1)
    assert fused[0].source == "rrf"


# ---------- KoreanResponseRules ----------


def test_korean_rules_appends_missing_sections() -> None:
    rules = KoreanResponseRules()
    out = rules.normalize("[원인]\n과부하")
    assert "[원인]" in out
    assert "[조치 절차]" in out
    assert "[관련 오류 코드]" in out


def test_korean_rules_passes_through_complete_response() -> None:
    rules = KoreanResponseRules()
    full = "[원인]\nx\n\n[조치 절차]\n1. y\n\n[관련 오류 코드]\nE-101"
    out = rules.normalize(full)
    assert out.count("[원인]") == 1
    assert out.count("[조치 절차]") == 1
    assert out.count("[관련 오류 코드]") == 1
