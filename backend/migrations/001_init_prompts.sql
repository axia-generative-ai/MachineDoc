-- 001_init_prompts.sql
-- 프롬프트 관리 테이블 (admin이 ai-service LLM 프롬프트를 hot-edit할 수 있도록).
-- ai-service의 prompt_service가 이 테이블에서 fetch (TTL 30s 캐시).

CREATE TABLE IF NOT EXISTS prompts (
  prompt_key   VARCHAR(64) PRIMARY KEY,
  content      TEXT NOT NULL,
  description  VARCHAR(255),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
