"""Hybrid 3-stage retrieval (Phase 6 rework — skeleton only).

Pipeline (per locked plan in `project_differentiation_plan.md`):

    [query]
      -> structured pre-filter (error_code -> equipment mapping)
      -> parallel: BM25 (PG tsvector) + Vector (pgvector HNSW)
      -> RRF merge
      -> Cross-encoder rerank (bge-reranker-base on RTX 4060)
      -> Top-K with parent-section attached

This file defines the **public surface and dataclasses**. The DB-backed
implementations (`BM25Searcher`, `VectorSearcher`) are intentionally thin:
they raise `NotImplementedError` so the file imports and unit-tests run
without a live PG. Wire them once the `manual_chunks_v2` schema lands.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Protocol, cast

from langchain_core.embeddings import Embeddings

from app.core.embeddings import get_embeddings
from app.core.vectorstore import V2Hit, VectorStore
from app.pipelines.chunking_v2 import SectionType, extract_error_codes_from_query

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Hit dataclass — what every searcher returns
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Hit:
    chunk_id: str
    parent_section_id: str
    manual_id: str
    equipment_id: str
    section_type: SectionType
    heading_path: tuple[str, ...]
    page: int
    chunk_text: str
    score: float
    source: str  # "bm25" | "vector" | "rrf" | "rerank"


# ---------------------------------------------------------------------------
# Stage 1 — structured pre-filter
# ---------------------------------------------------------------------------


@dataclass
class PreFilter:
    """Reduces the candidate set by structural metadata before retrieval.

    Inputs:
      - `error_code_to_equipment`: PRD A-02 mapping. When the query
        contains an error code, restrict retrieval to that equipment's
        manual(s).
      - `known_codes`: every code that appears anywhere in the corpus
        (including ambiguous codes that point to multiple equipments).
        Used to validate query tokens — a token is treated as a fault
        identifier ONLY if it appears in this set, which is what keeps
        the new permissive regex in `extract_error_codes_from_query`
        from leaking prose words ("the", "for", ...) into BM25 boost or
        equipment filtering.
      - `equipment_id` override from the API caller.

    Output is an `equipment_ids` allow-list (None = no filter).
    """

    error_code_to_equipment: dict[str, str] = field(default_factory=dict)
    known_codes: set[str] = field(default_factory=set)

    def resolve(
        self,
        query: str,
        *,
        equipment_id: str | None = None,
    ) -> list[str] | None:
        if equipment_id:
            return [equipment_id]
        codes = self.known_codes_in(query)
        eqs = sorted(
            {self.error_code_to_equipment[c] for c in codes if c in self.error_code_to_equipment}
        )
        return eqs or None

    def known_codes_in(self, query: str) -> tuple[str, ...]:
        """Return the subset of query tokens that exactly match a code in the
        known-codes set. Case is preserved by the corpus side (mnemonics
        like "FAn" / "oFA10" are case-sensitive in vendor displays).
        """
        candidates = extract_error_codes_from_query(query)
        if not self.known_codes:
            return candidates
        # exact match against the known-codes set
        return tuple(c for c in candidates if c in self.known_codes)

    @classmethod
    def from_store(cls, store: VectorStore | None = None) -> "PreFilter":
        """Build a PreFilter whose mapping AND known-code whitelist are
        derived from indexed data.

        Aggregates (code -> {equipment_id: section_count}) from
        `manual_sections.error_codes`. Codes pointing to a single equipment
        contribute to the equipment-filter mapping; codes that appear across
        multiple equipments are ambiguous (typically generic chapter numbers
        or short mnemonics shared by vendors) and are KEPT in `known_codes`
        but EXCLUDED from the equipment filter — so BM25 boost still works
        for them while avoiding wrong-manual bias.
        """
        store = store or VectorStore()
        observed: dict[str, dict[str, int]] = {}
        with store._connect() as conn, conn.cursor() as cur:  # noqa: SLF001
            cur.execute(
                """
                SELECT equipment_id, error_codes
                  FROM manual_sections
                 WHERE error_codes IS NOT NULL AND array_length(error_codes, 1) > 0
                """
            )
            for equipment_id, codes in cur.fetchall():
                for c in codes or ():
                    eq_counts = observed.setdefault(c, {})
                    eq_counts[equipment_id] = eq_counts.get(equipment_id, 0) + 1
        mapping: dict[str, str] = {
            c: next(iter(eqs))
            for c, eqs in observed.items()
            if len(eqs) == 1
        }
        known = set(observed.keys())
        ambiguous = len(observed) - len(mapping)
        logger.info(
            "PreFilter built from store",
            extra={
                "codes": len(mapping),
                "known_codes": len(known),
                "dropped_ambiguous": ambiguous,
            },
        )
        return cls(error_code_to_equipment=mapping, known_codes=known)


# ---------------------------------------------------------------------------
# Stage 2 — parallel searchers (skeletons; DB wiring later)
# ---------------------------------------------------------------------------


class Searcher(Protocol):
    """Common shape for BM25 / Vector / future searchers."""

    def search(
        self,
        query: str,
        *,
        equipment_ids: list[str] | None,
        k: int,
    ) -> list[Hit]: ...


def _v2hit_to_hit(h: V2Hit, source: str) -> Hit:
    return Hit(
        chunk_id=h.chunk_id,
        parent_section_id=h.parent_section_id,
        manual_id=h.manual_id,
        equipment_id=h.equipment_id,
        section_type=cast(SectionType, h.section_type),
        heading_path=h.heading_path,
        page=h.page,
        chunk_text=h.chunk_text,
        score=h.score,
        source=source,
    )


class BM25Searcher:
    """PostgreSQL `tsvector` + `ts_rank` keyword searcher.

    Hits the dual tsvector path on `manual_chunks_v2` — english (stemmed)
    UNION simple (identifier-preserving) so error codes like 'E-204',
    '40747', 'oFA10', 'FAn' don't get mangled by the english stemmer.
    """

    def __init__(
        self,
        store: VectorStore | None = None,
        *,
        known_codes: set[str] | None = None,
    ) -> None:
        self.store = store or VectorStore()
        self.known_codes = known_codes or set()

    def search(
        self,
        query: str,
        *,
        equipment_ids: list[str] | None,
        k: int,
    ) -> list[Hit]:
        identifier_terms = (
            [t for t in extract_error_codes_from_query(query) if t in self.known_codes]
            if self.known_codes
            else None
        )
        rows = self.store.search_bm25(
            query,
            k=k,
            equipment_ids=equipment_ids,
            identifier_terms=identifier_terms,
        )
        return [_v2hit_to_hit(h, source="bm25") for h in rows]


class VectorSearcher:
    """pgvector cosine-similarity searcher over child chunks."""

    def __init__(
        self,
        store: VectorStore | None = None,
        embedder: Embeddings | None = None,
    ) -> None:
        self.store = store or VectorStore()
        self.embedder = embedder or get_embeddings()

    def search(
        self,
        query: str,
        *,
        equipment_ids: list[str] | None,
        k: int,
    ) -> list[Hit]:
        query_vec = self.embedder.embed_query(query)
        rows = self.store.search_vector_v2(query_vec, k=k, equipment_ids=equipment_ids)
        return [_v2hit_to_hit(h, source="vector") for h in rows]


# ---------------------------------------------------------------------------
# Stage 3 — RRF merge
# ---------------------------------------------------------------------------


def reciprocal_rank_fusion(
    runs: list[list[Hit]],
    *,
    k: int,
    rrf_k: int = 60,
) -> list[Hit]:
    """Reciprocal Rank Fusion. `rrf_k=60` is the canonical default.

    Hits are de-duplicated by `chunk_id`; the surviving copy keeps the
    earliest source label so callers can still tell where it came from.
    """
    if not runs:
        return []
    scores: dict[str, float] = {}
    keep: dict[str, Hit] = {}
    for run in runs:
        for rank, hit in enumerate(run):
            scores[hit.chunk_id] = scores.get(hit.chunk_id, 0.0) + 1.0 / (rrf_k + rank + 1)
            keep.setdefault(hit.chunk_id, hit)

    fused = sorted(keep.values(), key=lambda h: scores[h.chunk_id], reverse=True)[:k]
    return [
        Hit(
            chunk_id=h.chunk_id,
            parent_section_id=h.parent_section_id,
            manual_id=h.manual_id,
            equipment_id=h.equipment_id,
            section_type=h.section_type,
            heading_path=h.heading_path,
            page=h.page,
            chunk_text=h.chunk_text,
            score=scores[h.chunk_id],
            source="rrf",
        )
        for h in fused
    ]


# ---------------------------------------------------------------------------
# Stage 4 — cross-encoder reranker (skeleton)
# ---------------------------------------------------------------------------


class Reranker:
    """bge-reranker-base wrapper.

    GPU target: NVIDIA RTX 4060 (laptop). Loaded lazily so import-time
    cost stays zero. Falls through to identity when the model is
    unavailable (CI, headless server) so unit tests keep working.
    """

    def __init__(
        self,
        model_name: str = "BAAI/bge-reranker-base",
        *,
        identifier_bonus: float = 1.5,
    ) -> None:
        self.model_name = model_name
        self.identifier_bonus = identifier_bonus
        self._model = None  # lazy

    def _ensure_loaded(self) -> None:
        if self._model is not None:
            return
        try:
            # Local import so absence of sentence-transformers / torch
            # doesn't break the rest of the module at import time.
            from sentence_transformers import CrossEncoder  # type: ignore

            self._model = CrossEncoder(self.model_name, max_length=512)
            logger.info("reranker loaded", extra={"model": self.model_name})
        except ImportError:
            logger.warning(
                "sentence-transformers not installed; reranker is identity passthrough"
            )
            self._model = "identity"  # sentinel

    def rerank(
        self,
        query: str,
        hits: list[Hit],
        *,
        top_k: int,
        identifier_terms: tuple[str, ...] | list[str] | None = None,
    ) -> list[Hit]:
        if not hits:
            return []
        self._ensure_loaded()
        if self._model == "identity" or self._model is None:
            return hits[:top_k]

        pairs = [(query, h.chunk_text) for h in hits]
        raw_scores = self._model.predict(pairs)  # type: ignore[union-attr]

        # Cross-encoders trained on natural-language pairs underweight bare
        # identifiers — the reranker can't tell that "20184" inside the chunk
        # is the answer the query asks for. When PreFilter has already vetted
        # the codes in the query, give a flat bonus to any hit whose text or
        # heading literally contains one of those codes. Heading match counts
        # because structure-aware chunking puts the code in the section title.
        ids = [t for t in (identifier_terms or ()) if t]
        adjusted: list[float] = []
        for h, s in zip(hits, raw_scores):
            base = float(s)
            if ids and self._hit_contains_identifier(h, ids):
                base += self.identifier_bonus
            adjusted.append(base)

        ordered = sorted(zip(hits, adjusted), key=lambda x: x[1], reverse=True)[:top_k]
        return [
            Hit(
                chunk_id=h.chunk_id,
                parent_section_id=h.parent_section_id,
                manual_id=h.manual_id,
                equipment_id=h.equipment_id,
                section_type=h.section_type,
                heading_path=h.heading_path,
                page=h.page,
                chunk_text=h.chunk_text,
                score=float(s),
                source="rerank",
            )
            for h, s in ordered
        ]

    @staticmethod
    def _hit_contains_identifier(h: Hit, ids: list[str]) -> bool:
        haystack_parts = [h.chunk_text or ""]
        haystack_parts.extend(h.heading_path or ())
        haystack = "\n".join(haystack_parts)
        return any(code and code in haystack for code in ids)


# ---------------------------------------------------------------------------
# Top-level orchestrator
# ---------------------------------------------------------------------------


@dataclass
class HybridRetriever:
    pre_filter: PreFilter
    bm25: BM25Searcher
    vector: VectorSearcher
    reranker: Reranker
    candidate_k: int = 20  # per-searcher k before RRF
    final_k: int = 3       # after rerank

    def retrieve(
        self,
        query: str,
        *,
        equipment_id: str | None = None,
        final_k: int | None = None,
    ) -> list[Hit]:
        equipment_ids = self.pre_filter.resolve(query, equipment_id=equipment_id)
        identifier_terms = self.pre_filter.known_codes_in(query)
        bm25_hits = self.bm25.search(query, equipment_ids=equipment_ids, k=self.candidate_k)
        vec_hits = self.vector.search(query, equipment_ids=equipment_ids, k=self.candidate_k)
        fused = reciprocal_rank_fusion([bm25_hits, vec_hits], k=self.candidate_k)
        return self.reranker.rerank(
            query,
            fused,
            top_k=final_k or self.final_k,
            identifier_terms=identifier_terms,
        )
