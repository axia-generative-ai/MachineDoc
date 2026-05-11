"""Centralised application settings.

All runtime configuration must be loaded through `get_settings()`. Modules
must not read environment variables directly — go through this module so the
provider-swap contract (Ollama <-> OpenAI) stays enforceable.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

LLMProvider = Literal["ollama", "openai"]
EmbeddingProvider = Literal["ollama", "openai"]
ChunkingStrategy = Literal["v1", "v2"]
PipelineVersion = Literal["v1", "v2"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ---- LLM ----
    llm_provider: LLMProvider = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    # Default LLM swapped 2026-05 from qwen3.5:9b to qwen2.5:3b — the
    # smaller model fits the dev box's RAM/latency budget for KPI runs.
    # Both share the /no_think prefix quirk (see project_qwen3_no_think
    # memory). Override via OLLAMA_MODEL env var.
    ollama_model: str = "qwen2.5:3b"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    # ---- Embeddings ----
    embedding_provider: EmbeddingProvider = "ollama"
    # nomic-embed-text (768d) replaced bge-m3 (1024d) after a
    # reproducible Ollama NaN failure on plain English input ("failed to
    # encode response: json: unsupported value: NaN" / status 500).
    # Do NOT revert to bge-m3 without first confirming the upstream fix.
    # Override via EMBEDDING_MODEL env var.
    embedding_model: str = "nomic-embed-text"
    openai_embedding_model: str = "text-embedding-3-small"

    # ---- Database ----
    # Default targets the compose db (ankane/pgvector:latest, PG15) bound
    # to host port 5433. Backend owner locked the smart_factory / ax_user
    # naming on 2026-05-09. The legacy host PG17 `MachineDoc` DB on
    # :5432 is kept only for backup. Override via DATABASE_URL env var.
    database_url: str = (
        "postgresql+psycopg://ax_user:9ASs4xPr0j3Ct@localhost:5433/smart_factory"
    )

    # ---- Server ----
    host: str = "0.0.0.0"
    # Port is 8001 to avoid colliding with backend (:8000) when both run
    # locally / in docker-compose. Locked at the 2026-05-08 integration sync.
    port: int = 8001
    log_level: str = "INFO"

    # ---- Pipeline tuning (used in later phases) ----
    chunk_size: int = Field(default=800, ge=100)
    chunk_overlap: int = Field(default=100, ge=0)
    retrieval_top_k: int = Field(default=3, ge=1)
    similarity_threshold: float = Field(default=0.3, ge=0.0, le=1.0)

    # ---- Phase 6: structure-aware chunking + hybrid retrieval ----
    # v2 is the production default since 2026-05. v1 kept for A/B
    # comparison only — the manual_chunks (v1) table is no longer
    # populated in the current corpus.
    chunking_strategy: ChunkingStrategy = "v2"
    v2_child_size: int = Field(default=600, ge=100)
    v2_child_overlap: int = Field(default=80, ge=0)

    # ---- Phase 6 wiring: which RAG pipeline serves /api/v1/search ----
    # "v1" → legacy RagPipeline (vector-only similarity search; archived).
    # "v2" → RagPipelineV2 (HybridRetriever with BM25 + vector + RRF +
    #        bge-reranker-base). Real-manual eval Top-3 100% (25/25)
    #        on the 8-vendor corpus as of 2026-05-09.
    pipeline_version: PipelineVersion = "v2"
    # When pipeline_version="v2", these tune HybridRetriever.
    v2_candidate_k: int = Field(default=20, ge=3)
    v2_final_k: int = Field(default=3, ge=1)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the singleton settings instance.

    Tests can clear the cache via `get_settings.cache_clear()` after
    monkeypatching environment variables.
    """
    return Settings()
