# FactoryGuard AI 서비스

스마트팩토리 설비 매뉴얼 RAG 검색과 이상감지 분석을 제공하는 AI 백엔드입니다. FactoryGuard 프로토타입의 AI 서비스 모듈로, 백엔드(FastAPI)와 프론트엔드(React)와 함께 풀스택을 구성합니다.

> **데모 일정**: 2026-05-13
> **현재 상태**: KPI Top-3 100% (25/25), 백엔드 통합 어댑터 완료, 풀스택 통합 검증 완료(모드 C)

## 핵심 기능

| 기능 | Endpoint | 비고 |
|---|---|---|
| 오류코드 → 매뉴얼 조치 절차 | `POST /api/v1/search` | 백엔드 contract, 한국어 응답 |
| 센서 로그 → 이상감지 분석 | `POST /api/v1/anomaly` | 룰엔진 + LLM 2단계 |
| 매뉴얼 PDF 업로드 + 자동 색인 | `POST /api/v1/ingest` | error_code 자동 추출, multipart |
| 설비/카테고리 기반 매뉴얼 추천 | `POST /api/v1/manuals/recommend` | LLM 없이 ~1초 |
| 헬스체크 | `GET /health` | liveness |

Swagger UI: `http://localhost:8001/docs`

## 기술 스택

| 계층 | 선택 |
|---|---|
| 런타임 | Python 3.10 ~ 3.12 (`pyproject.toml`: `>=3.10,<3.13`) |
| 웹 프레임워크 | FastAPI + Uvicorn |
| 패키지 매니저 | [uv](https://github.com/astral-sh/uv) |
| LLM (운영) | OpenAI `gpt-4o-mini` (데모용) |
| LLM (로컬 개발) | Ollama `qwen2.5:3b` (`/no_think` prefix 필수) |
| 임베딩 | Ollama `nomic-embed-text` (768차원) |
| 벡터 DB | PostgreSQL 15 + pgvector (HNSW, compose db 기준) |
| RAG 파이프라인 | 커스텀 hybrid (BM25 + Vector + RRF + bge-reranker-base) |
| Provider SDK | `langchain-core` + `langchain-ollama` / `langchain-openai` (provider 추상화 인터페이스만 사용) |
| PDF 파싱 | PyMuPDF (`fitz`) |

> **차별화 포인트**: LangChain의 RAG 추상화(`RetrievalQA`, vectorstore wrapper, document loader 등) 대신 직접 작성한 hybrid retrieval (BM25 + Vector + RRF + bge-reranker-base) + 구조 인지 청킹 + identifier-aware reranker. LangChain은 LLM/임베딩 provider 추상화 SDK로만 사용해 환경변수만으로 Ollama ⇄ OpenAI 전환이 가능합니다.

## 빠른 시작

### 1. 의존성 설치

```bash
cd ai-service
uv sync
```

### 2. 환경변수 설정

`.env.example`을 복사해서 `.env` 만들기 (`.env`는 gitignored):

```bash
cp .env.example .env
```

기본값은 로컬 개발용(Ollama + compose db)으로 설정되어 있어 별도 수정 없이 동작합니다. 참고용 핵심 키:

```env
# Provider 선택 (둘 다 ollama가 로컬 개발 기본값)
LLM_PROVIDER=ollama
EMBEDDING_PROVIDER=ollama

# Ollama 설정
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b
EMBEDDING_MODEL=nomic-embed-text

# DB (compose db 기준; 호스트 5433 바인딩)
DATABASE_URL=postgresql+psycopg://ax_user:9ASs4xPr0j3Ct@localhost:5433/smart_factory

# 서버
HOST=0.0.0.0
PORT=8001
LOG_LEVEL=INFO

# 파이프라인 (v2 = hybrid retrieval + reranker, 운영 기본값)
PIPELINE_VERSION=v2
CHUNKING_STRATEGY=v2
```

> 운영 기본값은 `app/config.py`와 `.env.example`에 정의되어 있습니다. 둘 다 동일하게 운영 기본값을 따릅니다 (qwen2.5:3b / nomic-embed-text / compose db / v2 파이프라인).

### 3. 외부 런타임 가동

| 런타임 | 가동 방법 |
|---|---|
| PostgreSQL 15 + pgvector 0.5.1 | Docker compose db (`docker compose up -d db`, ankane/pgvector:latest) — 호스트 5433에 바인딩. 또는 호스트 PG에 pgvector 설치하여 5433에 띄움 |
| Ollama | Ollama Desktop 실행 또는 `ollama serve` |
| 모델 pull | `ollama pull qwen2.5:3b && ollama pull nomic-embed-text` |

### 4. DB 초기화 (1회)

```bash
uv run python scripts/init_db.py
```

`manual_chunks`, `manual_sections`, `manual_chunks_v2` + 인덱스 + trigger를 생성합니다.

### 5. 매뉴얼 색인 (1회)

```bash
uv run python scripts/ingest_manuals_v2.py
```

`manuals/` 폴더의 8권 PDF를 파싱 → 청킹 → 임베딩 → 색인. 약 12분 소요(Yaskawa 936p 포함).

### 6. 서비스 가동

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8001
```

검증:

```bash
curl http://localhost:8001/health     # {"status":"ok"}
curl http://localhost:8001/docs       # Swagger UI
```

## 프로젝트 구조

```
ai-service/
├── app/
│   ├── main.py                 # FastAPI 엔트리포인트, /health, 라우터 등록
│   ├── config.py               # pydantic-settings 기반 환경변수
│   ├── core/                   # embeddings.py, llm.py, vectorstore.py, prompt_loader.py
│   ├── pipelines/
│   │   ├── chunking.py         # v1 — 페이지 단위 청킹 (legacy)
│   │   ├── chunking_v2.py      # v2 — 구조 인지 청킹 (heading/section)
│   │   ├── retrieval_v2.py     # PreFilter + BM25 + Vector + RRF + Reranker
│   │   ├── rag.py              # v1 RAG (legacy)
│   │   ├── rag_v2.py           # v2 RAG (현재 운영)
│   │   └── anomaly.py          # 룰엔진 + LLM 2단계
│   ├── api/                    # search.py, anomaly.py, ingest.py, recommend.py
│   ├── schemas/                # 요청/응답 Pydantic 모델
│   └── services/
│       ├── ingest_service.py   # PDF → 청킹 → 임베딩 → 색인 단일 진입점
│       └── fault_pattern_detector.py  # 매뉴얼별 fault pattern 추출 (ingest 보조)
├── data/
│   ├── anomaly_rules.json                    # 백엔드 EQ-XXX-NNN + DataType 기준 룰 20개
│   └── anomaly_rules.legacy_synthetic.json   # Phase 0~1 합성 룰 백업
├── manuals/                    # 실 영문 매뉴얼 8권 (gitignored — 저작권)
├── migrations/                 # 001_init_vectorstore.sql, 002_v2_structured_chunks.sql
├── scripts/                    # init_db.py, ingest_manuals_v2.py, pull_models.sh
├── tests/
│   ├── unit/                   # 46 tests
│   └── eval/                   # KPI 평가 (Top-3 25/25 = 100%)
├── pyproject.toml              # uv 기반
└── .env                        # gitignored
```

## API 사용 예시

### 오류코드 검색

```bash
curl -X POST http://localhost:8001/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"error_code":"10009"}'
```

응답:
```json
{
  "status": "success",
  "analysis": "### 원인\n작업 메모장이 가득 찼다는 오류 ...",
  "solution": "1. 프로그램을 저장하십시오 (출처: abb_irb_troubleshooting.pdf p81)\n2. 시스템을 다시 시작하십시오 (출처: abb_irb_troubleshooting.pdf p446)"
}
```

### 이상감지 분석

```bash
curl -X POST http://localhost:8001/api/v1/anomaly \
  -H "Content-Type: application/json" \
  -d '{
    "equipment_id":"EQ-MOTOR-001",
    "timestamp":"2026-05-09T10:00:00",
    "readings":{"TEMPERATURE":95.0,"VIBRATION":700.0}
  }'
```

응답:
```json
{
  "status": "이상",
  "analysis": "- 정밀 모터 본체 온도 70°C 초과 ...",
  "solution": "- 즉시 정지 후 윤활 점검 ..."
}
```

### 매뉴얼 추천

```bash
curl -X POST http://localhost:8001/api/v1/manuals/recommend \
  -H "Content-Type: application/json" \
  -d '{"equipment_id":"EQ-MOTOR-001","category":"점검","top_k":5}'
```

### PDF 업로드

```bash
curl -X POST http://localhost:8001/api/v1/ingest \
  -F "file=@manuals/abb_irb_troubleshooting.pdf" \
  -F "manual_id=abb_irb_troubleshooting" \
  -F "equipment_id=eq_abb_irb"
```

## 백엔드 통합

| 항목 | 값 |
|---|---|
| 포트 | ai-service `:8001` / 백엔드 `:8000` (분리) |
| DB | 단일 pgvector DB (백엔드와 공유, 테이블 namespace 분리) |
| 인증 | 없음 (백엔드 내부망 호출 가정) |
| ingest 처리 | 동기 (~113초/446p) |
| error_code sync | ai-service `/ingest` 응답의 `error_codes[]`를 백엔드가 자기 테이블에 INSERT |

자세한 contract와 백엔드 작업 항목은 `.claude/reports/2026-05-09_backend_handoff_requirements.md` 참고.

## KPI 현황

| 지표 | 목표 | 현재 |
|---|---|---|
| Top-3 정확도 | ≥ 80% | **100% (25/25)** |
| 검색 평균 응답 | ≤ 6초 | retrieval ~900ms + LLM 3~5초 |
| 이상감지 응답 | — | 정상 즉시 / 이상 ~5초 |
| 매뉴얼 추천 | — | ~1초 (LLM 없음) |

평가셋: `tests/eval/test_set_v2.json` (25 케이스).
러너: `uv run python tests/eval/run_eval_v2.py`.

## 프로바이더 전환 (Ollama ⇄ OpenAI)

모든 LLM/임베딩 호출은 `app/core/llm.py`, `app/core/embeddings.py`를 통과합니다. 환경변수만 바꾸면 코드 수정 없이 전환 가능:

```bash
# 로컬 개발
LLM_PROVIDER=ollama
EMBEDDING_PROVIDER=ollama

# 데모 / 운영
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
EMBEDDING_PROVIDER=openai
```

> ⚠️ **임베딩 차원 주의**: `nomic-embed-text`는 768차원, OpenAI `text-embedding-3-small`은 1536차원. 프로바이더 전환 시 pgvector 컬럼 타입과 인덱스 재생성이 필요합니다 (`migrations/`의 vector(768) 정의 변경 + 재색인).

## 개발 / 테스트

```bash
# 단위 테스트 (46개)
uv run pytest tests/unit -q

# KPI 평가
uv run python tests/eval/run_eval_v2.py

# 매뉴얼 재색인 (8권 ~12분)
uv run python scripts/ingest_manuals_v2.py
```

## 문서

작업 중 산출물 / 문서는 `.claude/`에 정리되어 있습니다 (gitignored, 개인 작업 공간):

- `.claude/status.md` — 현재 상태 SSOT
- `.claude/integration/` — 통합 테스트 가이드, Docker 셋업, DB 마이그레이션 runbook
- `.claude/phases/` — phase별 검증 가이드
- `.claude/flows/` — Mermaid 흐름도
- `.claude/schema/` — vector store 스키마
- `.claude/planning/` — WBS, 차별화 의사결정
- `.claude/reports/` — 통합 테스트 보고서, 핸드오프 문서, 기획서 vs 구현 체크리스트
- `.claude/education/` — 14강 학습 시리즈

## 라이선스

프로토타입 단계. 매뉴얼 PDF는 공개 자료 기반 (gitignored).
