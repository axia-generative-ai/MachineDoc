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
    ollama_model: str = "qwen3.5:9b"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    # ---- Embeddings ----
    embedding_provider: EmbeddingProvider = "ollama"
    # nomic-embed-text replaced bge-m3 after a reproducible Ollama NaN
    # failure on plain English input ("failed to encode response: json:
    # unsupported value: NaN" / status 500). Override via EMBEDDING_MODEL
    # env var if a future bge-m3 build fixes this.
    embedding_model: str = "nomic-embed-text"
    openai_embedding_model: str = "text-embedding-3-small"

    # ---- Database ----
    database_url: str = (
        "postgresql+psycopg://factoryguard:factoryguard@localhost:5432/factoryguard"
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
    chunking_strategy: ChunkingStrategy = "v1"
    v2_child_size: int = Field(default=600, ge=100)
    v2_child_overlap: int = Field(default=80, ge=0)

    # ---- Phase 6 wiring: which RAG pipeline serves /api/v1/search ----
    # "v1" → legacy RagPipeline (vector-only similarity search, ABB-style
    #        synthetic eval set tuning).
    # "v2" → RagPipelineV2 (HybridRetriever with BM25 + vector + RRF +
    #        bge-reranker-base, real-manual eval Top-3 92%).
    pipeline_version: PipelineVersion = "v1"
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
