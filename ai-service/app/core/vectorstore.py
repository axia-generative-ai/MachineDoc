"""pgvector-backed vectorstore for manual chunks.

Uses psycopg directly rather than SQLAlchemy because the queries we need
are narrow (insert + cosine-similarity Top-K) and the pgvector adapter is
straightforward.

Connection strings are read from `Settings.database_url`. We accept both
SQLAlchemy-style (`postgresql+psycopg://...`) and bare (`postgresql://...`)
URLs and normalise to the bare form for psycopg.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

import psycopg
from pgvector.psycopg import register_vector
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from app.config import Settings, get_settings
from app.pipelines.chunking import Chunk
from app.pipelines.chunking_v2 import Chunk as ChunkV2
from app.pipelines.chunking_v2 import Section

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SearchResult:
    chunk_id: str
    manual_id: str
    equipment_id: str
    page: int
    chunk_index: int
    chunk_text: str
    distance: float

    @property
    def similarity(self) -> float:
        # pgvector cosine distance is 1 - cosine_similarity.
        return 1.0 - self.distance


@dataclass(frozen=True)
class V2Hit:
    """Row shape returned by the v2 search methods.

    Mirrors the columns BM25Searcher / VectorSearcher need to assemble a
    retrieval_v2.Hit. `score` semantics depend on the source:
      - vector:  1 - cosine_distance  (higher is better)
      - bm25:    ts_rank_cd            (higher is better)
    """

    chunk_id: str
    parent_section_id: str
    manual_id: str
    equipment_id: str
    section_type: str
    heading_path: tuple[str, ...]
    page: int
    chunk_text: str
    score: float


_BM25_TOKEN_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9\-_]*")
# Identifier = either prefix-style (E-204, ALM-12) or 4+ digit run (40747).
# 3-digit runs are too noisy (page numbers, year fragments).
_BM25_IDENT_RE = re.compile(r"\b(?:[A-Za-z]{1,4}-\d{2,4}|\d{4,6})\b")


def _bm25_or_terms(query: str) -> list[str]:
    """Tokenize a query for OR-style tsquery construction.

    Keeps alphanumeric runs (and `-`/`_`) so identifiers like 'E-204' or
    '40747' survive intact. Returns lowercased deduped terms in order.
    """
    seen: set[str] = set()
    out: list[str] = []
    for tok in _BM25_TOKEN_RE.findall(query):
        t = tok.lower()
        if t in seen:
            continue
        seen.add(t)
        out.append(t)
    return out


def _bm25_identifier_terms(query: str) -> list[str]:
    """Subset of tokens that look like equipment/error identifiers.

    Used for BM25 score boosting so an exact identifier match outranks a
    chunk that merely shares the word 'error'. Lowercased + deduped.
    """
    seen: set[str] = set()
    out: list[str] = []
    for tok in _BM25_IDENT_RE.findall(query):
        t = tok.lower()
        if t in seen:
            continue
        seen.add(t)
        out.append(t)
    return out


def _normalise_dsn(url: str) -> str:
    """Strip SQLAlchemy-style driver prefix for psycopg."""
    if url.startswith("postgresql+psycopg://"):
        return "postgresql://" + url.split("://", 1)[1]
    if url.startswith("postgresql+psycopg2://"):
        return "postgresql://" + url.split("://", 1)[1]
    return url


class VectorStore:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._dsn = _normalise_dsn(self.settings.database_url)

    # ----- helpers -----

    def _connect(self) -> psycopg.Connection:
        conn = psycopg.connect(self._dsn, autocommit=True)
        register_vector(conn)
        return conn

    # ----- write -----

    def insert_chunks(self, pairs: Iterable[tuple[Chunk, list[float]]]) -> int:
        """Bulk insert (chunk, vector) pairs. Returns rows inserted."""
        rows = [
            (
                c.chunk_id,
                c.manual_id,
                c.equipment_id,
                c.page,
                c.chunk_index,
                c.chunk_text,
                vec,
                Jsonb({"source_file": c.source_file}),
            )
            for c, vec in pairs
        ]
        if not rows:
            return 0
        with self._connect() as conn, conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO manual_chunks
                    (id, manual_id, equipment_id, page, chunk_index,
                     chunk_text, embedding, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                rows,
            )
        logger.info("inserted chunks", extra={"count": len(rows)})
        return len(rows)

    def truncate(self) -> None:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE manual_chunks")

    # ----- v2 write -----

    def insert_sections(self, sections: Iterable[Section]) -> int:
        """Bulk insert parent sections. Returns rows inserted."""
        rows = [
            (
                s.section_id,
                s.manual_id,
                s.equipment_id,
                s.section_type,
                Jsonb(list(s.heading_path)),
                s.page_start,
                s.page_end,
                s.text,
                list(s.error_codes),
            )
            for s in sections
        ]
        if not rows:
            return 0
        with self._connect() as conn, conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO manual_sections
                    (section_id, manual_id, equipment_id, section_type,
                     heading_path, page_start, page_end, section_text, error_codes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (section_id) DO NOTHING
                """,
                rows,
            )
        logger.info("inserted v2 sections", extra={"count": len(rows)})
        return len(rows)

    def insert_chunks_v2(self, pairs: Iterable[tuple[ChunkV2, list[float]]]) -> int:
        """Bulk insert (v2 chunk, vector) pairs. tsvector columns are
        populated automatically by the BEFORE INSERT trigger."""
        rows = [
            (
                c.chunk_id,
                c.parent_section_id,
                c.manual_id,
                c.equipment_id,
                c.section_type,
                Jsonb(list(c.heading_path)),
                c.page,
                c.chunk_index,
                c.chunk_text,
                vec,
                list(c.error_codes),
                c.source_file,
            )
            for c, vec in pairs
        ]
        if not rows:
            return 0
        with self._connect() as conn, conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO manual_chunks_v2
                    (chunk_id, parent_section_id, manual_id, equipment_id,
                     section_type, heading_path, page, chunk_index,
                     chunk_text, embedding, error_codes, source_file)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (chunk_id) DO NOTHING
                """,
                rows,
            )
        logger.info("inserted v2 chunks", extra={"count": len(rows)})
        return len(rows)

    def truncate_v2(self) -> None:
        # TRUNCATE manual_sections also drops manual_chunks_v2 via CASCADE FK.
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE manual_sections CASCADE")

    # ----- read -----

    def similarity_search(
        self,
        query_vector: list[float],
        *,
        k: int | None = None,
        equipment_id: str | None = None,
    ) -> list[SearchResult]:
        """Return Top-K chunks by cosine distance, optionally scoped."""
        k = k or self.settings.retrieval_top_k
        # Cast the bind parameter to `vector` explicitly. psycopg's default
        # adapter sends Python lists as `double precision[]`, and pgvector's
        # `<=>` operator has no overload for that type — leading to
        # "operator does not exist: vector <=> double precision[]".
        sql = """
            SELECT id::text AS chunk_id,
                   manual_id, equipment_id, page, chunk_index, chunk_text,
                   embedding <=> %s::vector AS distance
              FROM manual_chunks
             {where}
          ORDER BY embedding <=> %s::vector
             LIMIT %s
        """
        params: list[Any]
        if equipment_id:
            sql = sql.format(where="WHERE equipment_id = %s")
            params = [query_vector, equipment_id, query_vector, k]
        else:
            sql = sql.format(where="")
            params = [query_vector, query_vector, k]

        with self._connect() as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
        return [SearchResult(**r) for r in rows]

    # ----- v2 read -----

    def search_vector_v2(
        self,
        query_vector: list[float],
        *,
        k: int,
        equipment_ids: list[str] | None = None,
    ) -> list[V2Hit]:
        """pgvector cosine search over manual_chunks_v2 child chunks."""
        params: list[Any] = [query_vector]
        where = ""
        if equipment_ids:
            where = "WHERE equipment_id = ANY(%s)"
            params.append(equipment_ids)
        params += [query_vector, k]
        sql = f"""
            SELECT chunk_id::text,
                   parent_section_id::text,
                   manual_id, equipment_id, section_type,
                   heading_path, page, chunk_text,
                   1 - (embedding <=> %s::vector) AS score
              FROM manual_chunks_v2
              {where}
          ORDER BY embedding <=> %s::vector
             LIMIT %s
        """
        return self._fetch_v2_hits(sql, params)

    def search_bm25(
        self,
        query: str,
        *,
        k: int,
        equipment_ids: list[str] | None = None,
        identifier_terms: list[str] | None = None,
    ) -> list[V2Hit]:
        """Hybrid keyword search: english (stemmed) ∪ simple (identifier-
        preserving) tsvector matches, OR-joined for partial recall.

        Identifier tokens (E-204, 40747, ALM-12, oFA10, FAn, SOF, ...) get a
        +10 score boost when matched in the simple tsvector. Without this an
        exact code match scores no higher than a chunk that just shares the
        word 'error', so vendor boilerplate drowns out the true target.

        `identifier_terms` lets the caller pass a vetted code list (e.g. the
        intersection of query tokens with `PreFilter.known_codes`). When
        omitted, the legacy regex `_bm25_identifier_terms` is used so old
        callers keep working — but the regex only catches a subset of vendor
        formats, so retrievers that have a known-codes whitelist available
        should always pass it explicitly.
        """
        terms = _bm25_or_terms(query)
        if not terms:
            return []
        tsq = " | ".join(terms)
        if identifier_terms is not None:
            ids = [t.lower() for t in identifier_terms if t]
        else:
            ids = _bm25_identifier_terms(query)
        id_tsq = " | ".join(ids) if ids else None

        select_score = (
            "ts_rank_cd(tsv_english, to_tsquery('pg_catalog.english', %s))"
            " + ts_rank_cd(tsv_simple,  to_tsquery('pg_catalog.simple',  %s))"
        )
        score_params: list[Any] = [tsq, tsq]
        if id_tsq:
            select_score += (
                " + 10.0 * (CASE WHEN tsv_simple @@ to_tsquery('pg_catalog.simple', %s)"
                " THEN 1 ELSE 0 END)"
            )
            score_params.append(id_tsq)

        where_params: list[Any] = [tsq, tsq]
        where_clauses = [
            "(tsv_english @@ to_tsquery('pg_catalog.english', %s)"
            " OR tsv_simple  @@ to_tsquery('pg_catalog.simple',  %s))"
        ]
        if equipment_ids:
            where_clauses.append("equipment_id = ANY(%s)")
            where_params.append(equipment_ids)
        where_sql = " AND ".join(where_clauses)

        sql = f"""
            SELECT chunk_id::text,
                   parent_section_id::text,
                   manual_id, equipment_id, section_type,
                   heading_path, page, chunk_text,
                   ({select_score}) AS score
              FROM manual_chunks_v2
             WHERE {where_sql}
          ORDER BY score DESC
             LIMIT %s
        """
        return self._fetch_v2_hits(sql, [*score_params, *where_params, k])

    def fetch_section(self, section_id: str) -> dict[str, Any] | None:
        """Fetch one parent section by id. Used by RAG to assemble the
        full procedure/warning text after retrieving a child chunk."""
        with self._connect() as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT section_id::text, manual_id, equipment_id, section_type,
                       heading_path, page_start, page_end, section_text,
                       error_codes
                  FROM manual_sections
                 WHERE section_id = %s
                """,
                (section_id,),
            )
            return cur.fetchone()

    def _fetch_v2_hits(self, sql: str, params: list[Any]) -> list[V2Hit]:
        with self._connect() as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
        return [
            V2Hit(
                chunk_id=r["chunk_id"],
                parent_section_id=r["parent_section_id"],
                manual_id=r["manual_id"],
                equipment_id=r["equipment_id"],
                section_type=r["section_type"],
                heading_path=tuple(r["heading_path"] or ()),
                page=r["page"],
                chunk_text=r["chunk_text"],
                score=float(r["score"]),
            )
            for r in rows
        ]

    # ----- diagnostics -----

    def count(self) -> int:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM manual_chunks")
            (n,) = cur.fetchone()
            return n

    def count_v2(self) -> tuple[int, int]:
        """(sections, chunks_v2) row counts."""
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM manual_sections")
            (s,) = cur.fetchone()
            cur.execute("SELECT COUNT(*) FROM manual_chunks_v2")
            (c,) = cur.fetchone()
            return s, c
