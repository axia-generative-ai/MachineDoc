"""Prompt store backed by the shared `prompts` table.

ai-service used to embed prompt skeletons as Python literals (`_KOREAN_SKELETON`).
Admin-side editing required code changes + redeploy. This service externalises
prompts to the DB so the admin UI (backend → ai-service proxy) can hot-edit.

A 30-second in-process cache keeps query-time latency unchanged; default text
is returned when the row is missing or DB is briefly unreachable so the
pipeline never crashes on cold start.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from typing import Optional

import psycopg

from app.config import get_settings
from app.core.vectorstore import _normalise_dsn  # type: ignore[attr-defined]

log = logging.getLogger(__name__)

_CACHE_TTL_S = 30.0


@dataclass
class PromptRecord:
    key: str
    content: str
    description: Optional[str]
    updated_at: Optional[str]


class PromptService:
    def __init__(self) -> None:
        self._cache: dict[str, tuple[float, PromptRecord]] = {}
        self._lock = threading.Lock()

    def _dsn(self) -> str:
        return _normalise_dsn(get_settings().database_url)

    def _fetch(self, key: str) -> Optional[PromptRecord]:
        with psycopg.connect(self._dsn(), autocommit=True) as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT prompt_key, content, description, updated_at::text FROM prompts WHERE prompt_key = %s",
                (key,),
            )
            row = cur.fetchone()
        if not row:
            return None
        return PromptRecord(key=row[0], content=row[1], description=row[2], updated_at=row[3])

    def get(self, key: str, *, default: str) -> str:
        """캐시 또는 DB에서 prompt content를 가져온다. 없으면 default를 자동 INSERT."""
        now = time.monotonic()
        with self._lock:
            hit = self._cache.get(key)
        if hit and (now - hit[0]) < _CACHE_TTL_S:
            return hit[1].content

        try:
            record = self._fetch(key)
        except Exception as exc:  # noqa: BLE001
            log.warning("prompt fetch failed (%s) — fallback to default", exc)
            return default

        if record is None:
            # 첫 접근 시 default를 시드로 INSERT (관리자 페이지에서 편집 가능해지도록)
            try:
                self.upsert(key, default, description=f"auto-seeded for {key}")
                record = PromptRecord(key=key, content=default, description=None, updated_at=None)
            except Exception as exc:  # noqa: BLE001
                log.warning("prompt seed failed (%s) — fallback to default", exc)
                return default

        with self._lock:
            self._cache[key] = (now, record)
        return record.content

    def list_all(self) -> list[PromptRecord]:
        with psycopg.connect(self._dsn(), autocommit=True) as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT prompt_key, content, description, updated_at::text FROM prompts ORDER BY prompt_key"
            )
            rows = cur.fetchall()
        return [PromptRecord(key=r[0], content=r[1], description=r[2], updated_at=r[3]) for r in rows]

    def upsert(self, key: str, content: str, *, description: Optional[str] = None) -> PromptRecord:
        with psycopg.connect(self._dsn(), autocommit=True) as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO prompts (prompt_key, content, description, updated_at)
                VALUES (%s, %s, %s, now())
                ON CONFLICT (prompt_key)
                DO UPDATE SET content = EXCLUDED.content,
                              description = COALESCE(EXCLUDED.description, prompts.description),
                              updated_at = now()
                RETURNING prompt_key, content, description, updated_at::text
                """,
                (key, content, description),
            )
            row = cur.fetchone()
        record = PromptRecord(key=row[0], content=row[1], description=row[2], updated_at=row[3])
        with self._lock:
            self._cache[key] = (time.monotonic(), record)
        return record

    def invalidate(self, key: Optional[str] = None) -> None:
        with self._lock:
            if key is None:
                self._cache.clear()
            else:
                self._cache.pop(key, None)


prompt_service = PromptService()
