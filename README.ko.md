# 🏭 MachineDoc

> **스마트팩토리 설비 이상감지·매뉴얼 RAG AI 프로토타입**

[English Version](./README.md)

---

## 📖 프로젝트 소개

제조 현장에서 설비 오류코드 발생 시 해당 매뉴얼을 RAG 기반으로 즉각 제공하고, 가상 센서 로그 분석을 통해 이상 원인을 추정·조치 절차를 자동 안내하는 AI 서비스입니다.

### 핵심 가치

- 🔍 현장 매뉴얼 검색 시간 5~15분 → 즉시 (10초 이내)
- 👷 비숙련 작업자도 즉시 표준화된 조치 가이드 제공
- 📚 RAG 기반 출처 명시로 환각(hallucination) 방지

---

## 🎯 주요 기능

| 기능 | 설명 |
|---|---|
| 오류코드 검색 | 오류코드 입력 → 관련 매뉴얼 페이지 즉시 제공 |
| 설비 매뉴얼 조회 | 설비명·카테고리 기반 매뉴얼 검색 |
| 이상감지 시연 | 가상 로그 입력 → LLM 분석 → 이상 여부·원인 추정 |
| 조치 절차 가이드 | RAG + LLM 요약으로 단계별 조치 절차 표시 |
| 매뉴얼 관리 | PDF 업로드 → 청킹·임베딩 자동 처리 (관리자) |

---

## 📂 레포지토리 구조

```
.
├── frontend/        # React 18 + Vite + TypeScript (포트 5173)
├── backend/         # FastAPI + SQLAlchemy + JWT (포트 8000)
├── ai-service/      # FastAPI + LangChain + 커스텀 hybrid RAG (포트 8001)
├── docker-compose.yml
├── shared/          # 환경 변수 템플릿 등
└── docs/            # 기획·설계·아키텍처·발표 문서
```

각 폴더의 상세 구조·내부 모듈 설계는 `ai-service/README.md` 참고 (백엔드/프론트는 각각 본 README의 실행 섹션 참조).

---

## 👥 팀 구성

| 역할 | 담당 |
|---|---|
| Frontend | 팀원 A |
| Backend | 팀원 B |
| AI · ML | 팀원 C |

---

## 📅 개발 일정

| 단계 | 기간 | 주요 산출물 |
|---|---|---|
| 1단계 — 기획·설계 | 4/26 ~ 4/29 | PRD, WBS, 와이어프레임, API 명세 |
| 2단계 — MVP 개발 | 4/30 ~ 5/4 | FE 화면, BE API, AI RAG 독립 동작 |
| 3단계 — AI 통합·고도화 | 5/5 ~ 5/9 | 통합 + 이상감지 + 정확도 80%+ |
| 4단계 — QA·발표 준비 | 5/10 ~ 5/13 | 테스트, 발표 자료, 데모 |

---

## 🛠️ 기술 스택

| 영역 | 스택 |
|---|---|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| Backend | FastAPI, Python 3.13, SQLAlchemy, JWT |
| AI/ML | LangChain (provider SDK only), OpenAI API (운영), Ollama `qwen2.5:3b` + `nomic-embed-text` (로컬), bge-reranker-base, 커스텀 hybrid RAG |
| Database | PostgreSQL 15 + pgvector (HNSW) |
| DevOps | GitHub Actions, Docker Compose |

---

## ⚙️ 사전 설치 항목

| 도구 | 버전 | 설치 가이드 |
|---|---|---|
| **Git** | 2.40+ | https://git-scm.com/downloads |
| **Docker Desktop** | 4.x | https://www.docker.com/products/docker-desktop — Postgres+pgvector 컨테이너 실행용 |
| **Node.js** | 18+ (권장 20 LTS) | https://nodejs.org — 프론트 실행 |
| **Python** | **3.10 이상 3.13 미만** | https://www.python.org/downloads/ — backend는 3.13도 가능, ai-service는 `>=3.10,<3.13` 제약 |
| **uv** (ai-service 패키지 매니저) | 최신 | https://docs.astral.sh/uv/getting-started/installation/ — `pip install uv` 또는 `winget install astral-sh.uv` |
| **Ollama** (로컬 LLM 런타임) | 0.3+ | https://ollama.com/download — 로컬 개발용 LLM/임베딩 |

> Postgres·pgvector는 Docker 컨테이너로 띄우므로 호스트에 별도 설치 불필요.
> 운영(데모) 모드에서는 Ollama 대신 OpenAI API를 쓸 수 있습니다 (ai-service `.env`의 `LLM_PROVIDER=openai`).

---

## 🚀 빠른 시작 (로컬 개발)

### 0. 클론 + 환경 변수

```bash
git clone <repo-url> MachineDoc
cd MachineDoc

# 루트 .env (docker-compose가 사용)
cat > .env <<'EOF'
DB_USER=ax_user
DB_PASSWORD=9ASs4xPr0j3Ct
DB_NAME=smart_factory
DB_HOST=db
DB_PORT=5433
DATABASE_URL=postgresql://ax_user:9ASs4xPr0j3Ct@db:5432/smart_factory
EOF
```

`backend/.env`, `ai-service/.env`, `frontend/.env` 도 각각 필요. 템플릿이 없는 경우 다음 키를 채워 만드세요.

```env
# backend/.env
DATABASE_URL=postgresql://ax_user:9ASs4xPr0j3Ct@localhost:5433/smart_factory
SECRET_KEY=dev-only-secret-key-do-not-use-in-prod-32bytes-min
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
APP_ENV=development
AI_SERVICE_URL=http://localhost:8001
# 매뉴얼 PDF 저장 위치 — ai-service/manuals 공유 (ingest 동기 호출 + 색인 소스).
# 미지정 시 backend가 자동 탐지하지만, 배포 안정성 위해 명시 권장.
MANUAL_DIR=../ai-service/manuals

# frontend/.env (Vite는 VITE_ 접두어가 붙은 변수만 읽음)
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws/v1

# ai-service/.env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b
EMBEDDING_PROVIDER=ollama
EMBEDDING_MODEL=nomic-embed-text
DATABASE_URL=postgresql+psycopg://ax_user:9ASs4xPr0j3Ct@localhost:5433/smart_factory
HOST=0.0.0.0
PORT=8001
LOG_LEVEL=INFO
PIPELINE_VERSION=v2
CHUNKING_STRATEGY=v2
```

### 1. Postgres + pgvector 컨테이너 기동

```bash
docker compose up -d db
# 호스트 5433 → 컨테이너 5432로 매핑됨 (충돌 방지)
```

### 2. 마이그레이션 + 시드 적용

```bash
# 1) 스키마 생성 (backend가 SQLAlchemy `Base.metadata.create_all`로 처음 부팅 시 자동 생성)
# 2) 추가 마이그레이션 SQL
docker exec -i smart_factory_db psql -U ax_user -d smart_factory < backend/migrations/001_init_prompts.sql
docker exec -i smart_factory_db psql -U ax_user -d smart_factory < backend/migrations/002_add_saved_manual_equipment_id.sql
docker exec -i smart_factory_db psql -U ax_user -d smart_factory < backend/migrations/003_rename_notification_occured_at.sql

# 3) 시연용 시드 (설비 5종 + 매뉴얼 5건 + 시연 25개 오류코드 + 24h 로그/알림)
docker exec -i smart_factory_db psql -U ax_user -d smart_factory < backend/seeds/demo.sql
```

### 3. Ollama 모델 사전 다운로드 (로컬 개발 시)

```bash
ollama serve &              # 포트 11434
ollama pull qwen2.5:3b      # LLM (~2GB)
ollama pull nomic-embed-text  # 임베딩 (~274MB)
```

### 4. 각 서비스 기동

세 개 터미널을 열어 각각 실행 (로컬 dev — 핫 리로드).

#### 4-1. backend (포트 8000)

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate          # Windows (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
uvicorn app.main:app --port 8000 --reload --workers 1
```

> **--workers 1 강제**: WebSocket broadcast가 in-process `ConnectionManager` 기반이라 멀티 워커 시 다른 워커 connection으로 broadcast 안 됨.

#### 4-2. ai-service (포트 8001)

```bash
cd ai-service
uv sync                          # 가상환경 자동 생성 + 의존성 설치
uv run uvicorn app.main:app --host 0.0.0.0 --port 8001
```

> 기동 시 두 startup hook이 자동 실행: `_warmup_embedder` (Ollama 임베딩 모델 페이징) + `_warmup_retrieval` (RAG 파이프라인 빌드 + 더미 retrieval, cold-start 503 방지). 첫 부팅은 30~60초 소요.

#### 4-3. frontend (포트 5173)

```bash
cd frontend
npm install
npm run dev
```

브라우저에서 http://localhost:5173 접속.

### 5. PDF 매뉴얼 색인 (선택)

`ai-service/manuals/` 안 8개 PDF는 사전에 색인되어 있어야 RAG가 답합니다. 시드 DB가 이미 있다면 스킵, 처음 셋업하는 경우 어드민 매뉴얼 등록 UI(`POST /api/v1/manual/upload` → backend가 ai-service `/ingest`로 위임)나 ai-service README의 일괄 색인 스크립트를 사용하세요.

> 백엔드는 업로드 시 **원본 파일명**(예: `ga700.pdf`)을 그대로 `saved_manual.file_url`에 저장하고, ai-service도 동일 값을 `manual_chunks_v2.source_file`에 기록합니다. 이 두 컬럼이 일치해야 검색 인용→PDF 열기가 정상 동작합니다. ingest 성공 시 ai-service가 파일명 매핑 + retrieval 캐시를 자동 무효화하므로 새 매뉴얼이 바로 검색됩니다.

---

## 🐳 Docker Compose 일괄 기동 (대안)

호스트에 Python/Node를 안 깔고 다 컨테이너로 띄우려면:

```bash
docker compose up -d
```

> 단, frontend는 `docker-compose.yml`에 정의돼 있지 않으므로 호스트에서 `npm run dev` 별도 실행 필요. Ollama도 호스트에서 따로 띄워야 함 (compose 컨테이너는 `host.docker.internal:11434`로 접근).

---

## 🧪 동작 검증 (스모크 테스트)

| 대상 | 명령 | 기대 결과 |
|---|---|---|
| ai-service health | `curl http://localhost:8001/health` | `{"status":"ok"}` |
| ai-service RAG | `curl -X POST http://localhost:8001/api/v1/search -H "Content-Type: application/json" -d '{"error_code":"E5"}'` | `status:success` + ga700.pdf 인용 |
| backend docs | http://localhost:8000/docs | Swagger UI |
| frontend | http://localhost:5173 | 로그인 화면 |

시연용 오류코드 25개는 `ai-service/.claude/planning/demo_error_codes_25.md` 참고 (gitignored, 발표자 전용).

---

## 📄 라이선스

이 프로젝트는 포트폴리오 목적의 프로토타입입니다.

---
