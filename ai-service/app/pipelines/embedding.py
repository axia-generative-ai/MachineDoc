"""Batch embedding for chunked manual text.

All embedding access goes through `app.core.embeddings.get_embeddings()`
so the Ollama <-> OpenAI swap stays environment-only.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Iterable, Sequence

from langchain_core.embeddings import Embeddings
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.embeddings import get_embeddings
from app.pipelines.chunking import Chunk
from app.pipelines.chunking_v2 import Chunk as ChunkV2

logger = logging.getLogger(__name__)

DEFAULT_BATCH_SIZE = 32
# Minimum *alphanumeric* length after PUA/control sanitization. bge-m3 returns
# NaN (Ollama 500) on empty/whitespace input AND on inputs that are pure
# punctuation/numbers like '3.1.1' — anything below this threshold has no
# retrieval signal worth embedding.
_MIN_EMBED_ALNUM = 5


def _sanitize_for_embedding(text: str) -> str:
    """Strip Private-Use-Area glyphs (e.g. '\\uf0b7' bullet from Symbol font)
    and other control chars that bge-m3 can choke on, returning a clean
    string. Keeps newlines/tabs."""
    out = []
    for ch in text:
        cp = ord(ch)
        if 0xE000 <= cp <= 0xF8FF:  # Private Use Area
            continue
        if cp < 32 and ch not in "\n\r\t":
            continue
        out.append(ch)
    return "".join(out)


def _is_embeddable(text: str) -> bool:
    """True if the text has enough alphanumeric content for a meaningful
    embedding. Filters out heading numbers, bullet stubs, blank lines."""
    alnum = sum(1 for ch in text if ch.isalnum())
    return alnum >= _MIN_EMBED_ALNUM


@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type(Exception),
)
def _embed_batch(embedder: Embeddings, texts: Sequence[str]) -> list[list[float]]:
    return embedder.embed_documents(list(texts))


def embed_chunks(
    chunks: Iterable[Chunk],
    *,
    embedder: Embeddings | None = None,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> list[tuple[Chunk, list[float]]]:
    """Embed an iterable of chunks; returns (chunk, vector) pairs.

    Logs throughput (chunks/second) so AI-15 latency baselining can read
    the numbers from app logs without re-running embedding.
    """
    embedder = embedder or get_embeddings()
    chunk_list = list(chunks)
    if not chunk_list:
        return []

    results: list[tuple[Chunk, list[float]]] = []
    start = time.perf_counter()
    for i in range(0, len(chunk_list), batch_size):
        batch = chunk_list[i : i + batch_size]
        vectors = _embed_batch(embedder, [c.chunk_text for c in batch])
        if len(vectors) != len(batch):
            raise RuntimeError(
                f"embedding count mismatch: got {len(vectors)} for {len(batch)} chunks"
            )
        results.extend(zip(batch, vectors))

    elapsed = time.perf_counter() - start
    rate = len(chunk_list) / elapsed if elapsed > 0 else float("inf")
    dim = len(results[0][1]) if results else 0
    logger.info(
        "embedded chunks",
        extra={
            "count": len(chunk_list),
            "elapsed_s": round(elapsed, 2),
            "chunks_per_s": round(rate, 1),
            "dim": dim,
        },
    )
    return results


def embed_chunks_v2(
    chunks: Iterable[ChunkV2],
    *,
    embedder: Embeddings | None = None,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> list[tuple[ChunkV2, list[float]]]:
    """v2 counterpart of `embed_chunks` — same batching/retry semantics
    but typed for the structure-aware ChunkV2.

    Two-step pre-filter prevents the bge-m3 NaN-on-Ollama-500 failure:
      1. Sanitize each chunk_text (strip Private-Use-Area glyphs from
         Symbol-font bullets, control chars).
      2. Drop chunks with too few alphanumeric chars (heading stubs like
         '3.1.1', empty fragments) — these embed to NaN even sanitized.
    """
    embedder = embedder or get_embeddings()
    raw = list(chunks)
    sanitized: list[ChunkV2] = []
    for c in raw:
        cleaned = _sanitize_for_embedding(c.chunk_text)
        if not _is_embeddable(cleaned):
            continue
        if cleaned == c.chunk_text:
            sanitized.append(c)
        else:
            from dataclasses import replace as _replace
            sanitized.append(_replace(c, chunk_text=cleaned))
    chunk_list = sanitized
    dropped = len(raw) - len(chunk_list)
    if dropped:
        logger.info("dropped %d unembeddable v2 chunks (heading stubs / PUA-only)", dropped)
    if not chunk_list:
        return []

    results: list[tuple[ChunkV2, list[float]]] = []
    start = time.perf_counter()
    for i in range(0, len(chunk_list), batch_size):
        batch = chunk_list[i : i + batch_size]
        vectors = _embed_batch(embedder, [c.chunk_text for c in batch])
        if len(vectors) != len(batch):
            raise RuntimeError(
                f"embedding count mismatch: got {len(vectors)} for {len(batch)} chunks"
            )
        results.extend(zip(batch, vectors))

    elapsed = time.perf_counter() - start
    rate = len(chunk_list) / elapsed if elapsed > 0 else float("inf")
    dim = len(results[0][1]) if results else 0
    logger.info(
        "embedded v2 chunks",
        extra={
            "count": len(chunk_list),
            "elapsed_s": round(elapsed, 2),
            "chunks_per_s": round(rate, 1),
            "dim": dim,
        },
    )
    return results


def embedding_dimension(embedder: Embeddings | None = None) -> int:
    """Probe the configured embedder for its output dimensionality.

    Used by the migration script and the vectorstore to size the
    pgvector column correctly.
    """
    embedder = embedder or get_embeddings()
    vec = embedder.embed_query("dimension probe")
    return len(vec)
