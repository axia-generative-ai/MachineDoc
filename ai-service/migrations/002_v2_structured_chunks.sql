-- 002_v2_structured_chunks.sql
--
-- Phase 6 schema for structure-aware chunking + hybrid retrieval.
--
-- Two new tables, both independent from v1's `manual_chunks` so the v1
-- pipeline stays an A/B baseline:
--
--   manual_sections    -- parent sections (one logical region of a manual)
--   manual_chunks_v2   -- child chunks (the units that actually get embedded)
--
-- Retrieval flow:
--   - BM25 + vector search both run against `manual_chunks_v2`
--   - After top-k merge, the parent section is fetched from
--     `manual_sections` and attached as LLM context
--
-- Embedding column dim is provider-dependent — same `__EMBEDDING_DIM__`
-- placeholder pattern as 001 (substituted by scripts/init_db.py).

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ---------------------------------------------------------------------------
-- Parent sections
-- ---------------------------------------------------------------------------
-- Holds the full text of a logical region (procedure / warning / spec /
-- narrative / table / error). Sections may span multiple pages — page_start
-- and page_end are inclusive 1-indexed.
--
-- `heading_path` is the breadcrumb chain from chunking_v2.Section
-- (e.g. ['6 Trouble shooting by Event log', '40747, Access Error']).
-- Stored as JSONB array so callers can reconstruct it without parsing.
--
-- `error_codes` is a normalized text[] (e.g. ['40747', 'E-204']) for fast
-- equality lookup via GIN. Source-of-truth for code → section linking.

CREATE TABLE IF NOT EXISTS manual_sections (
    section_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    manual_id       TEXT NOT NULL,
    equipment_id    TEXT NOT NULL,
    section_type    TEXT NOT NULL
                    CHECK (section_type IN ('procedure','warning','spec','narrative','table','error')),
    heading_path    JSONB NOT NULL DEFAULT '[]'::jsonb,
    page_start      INT  NOT NULL,
    page_end        INT  NOT NULL,
    section_text    TEXT NOT NULL,
    error_codes     TEXT[] NOT NULL DEFAULT '{}',
    source_file     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS manual_sections_manual_id
    ON manual_sections (manual_id);
CREATE INDEX IF NOT EXISTS manual_sections_equipment_id
    ON manual_sections (equipment_id);
CREATE INDEX IF NOT EXISTS manual_sections_section_type
    ON manual_sections (section_type);
CREATE INDEX IF NOT EXISTS manual_sections_error_codes_gin
    ON manual_sections USING GIN (error_codes);

-- ---------------------------------------------------------------------------
-- Child chunks (the unit that gets embedded + indexed)
-- ---------------------------------------------------------------------------
-- Mirrors a subset of the parent section's metadata so retrieval can return
-- everything needed to assemble a Hit (see retrieval_v2.Hit) without a join.
-- The actual parent text is fetched lazily via parent_section_id only when
-- the LLM needs it.
--
-- Two tsvector columns by design:
--   tsv_english   -- stemmed, English text-search config (recall on natural
--                    language queries)
--   tsv_simple    -- no stemmer/stopwords, preserves identifiers like
--                    'E-204' or '40747' (retrieval_v2.BM25Searcher comment
--                    flagged that the english config mangles error codes)
--
-- Both populated by a BEFORE INSERT/UPDATE trigger so callers don't have
-- to maintain them.

CREATE TABLE IF NOT EXISTS manual_chunks_v2 (
    chunk_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_section_id   UUID NOT NULL
                        REFERENCES manual_sections(section_id) ON DELETE CASCADE,
    manual_id           TEXT NOT NULL,
    equipment_id        TEXT NOT NULL,
    section_type        TEXT NOT NULL
                        CHECK (section_type IN ('procedure','warning','spec','narrative','table','error')),
    heading_path        JSONB NOT NULL DEFAULT '[]'::jsonb,
    page                INT  NOT NULL,
    chunk_index         INT  NOT NULL,
    chunk_text          TEXT NOT NULL,
    embedding           VECTOR(__EMBEDDING_DIM__) NOT NULL,
    error_codes         TEXT[] NOT NULL DEFAULT '{}',
    source_file         TEXT,
    tsv_english         TSVECTOR,
    tsv_simple          TSVECTOR,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Cosine distance HNSW (matches retrieval_v2.VectorSearcher comment).
CREATE INDEX IF NOT EXISTS manual_chunks_v2_embedding_hnsw
    ON manual_chunks_v2 USING hnsw (embedding vector_cosine_ops);

-- BM25 path: GIN over both tsvectors.
CREATE INDEX IF NOT EXISTS manual_chunks_v2_tsv_english_gin
    ON manual_chunks_v2 USING GIN (tsv_english);
CREATE INDEX IF NOT EXISTS manual_chunks_v2_tsv_simple_gin
    ON manual_chunks_v2 USING GIN (tsv_simple);

-- Pre-filter (equipment scope, error-code lookup) and parent join.
CREATE INDEX IF NOT EXISTS manual_chunks_v2_equipment_id
    ON manual_chunks_v2 (equipment_id);
CREATE INDEX IF NOT EXISTS manual_chunks_v2_manual_id
    ON manual_chunks_v2 (manual_id);
CREATE INDEX IF NOT EXISTS manual_chunks_v2_parent_section_id
    ON manual_chunks_v2 (parent_section_id);
CREATE INDEX IF NOT EXISTS manual_chunks_v2_error_codes_gin
    ON manual_chunks_v2 USING GIN (error_codes);

-- ---------------------------------------------------------------------------
-- tsvector trigger
-- ---------------------------------------------------------------------------
-- Keeps tsv_english and tsv_simple in sync with chunk_text on every
-- INSERT/UPDATE. heading_path joined into the english vector with weight
-- A so heading hits rank above body hits; chunk_text gets weight B.
-- The simple vector indexes only the body text — its purpose is exact
-- token preservation for identifier lookups (error codes), not weighting.

CREATE OR REPLACE FUNCTION manual_chunks_v2_tsv_refresh() RETURNS trigger AS $$
DECLARE
    headings_text TEXT;
BEGIN
    SELECT COALESCE(string_agg(value, ' '), '')
      INTO headings_text
      FROM jsonb_array_elements_text(NEW.heading_path);

    NEW.tsv_english :=
        setweight(to_tsvector('pg_catalog.english', COALESCE(headings_text, '')), 'A') ||
        setweight(to_tsvector('pg_catalog.english', COALESCE(NEW.chunk_text, '')), 'B');
    NEW.tsv_simple :=
        to_tsvector('pg_catalog.simple', COALESCE(NEW.chunk_text, ''));
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS manual_chunks_v2_tsv_trigger ON manual_chunks_v2;
CREATE TRIGGER manual_chunks_v2_tsv_trigger
    BEFORE INSERT OR UPDATE OF chunk_text, heading_path
    ON manual_chunks_v2
    FOR EACH ROW EXECUTE FUNCTION manual_chunks_v2_tsv_refresh();
