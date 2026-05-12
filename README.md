# 🏭 MachineDoc

> **Smart Factory Anomaly Detection & RAG-based Manual Retrieval AI Prototype**

[한국어 버전](./README.ko.md)

---

## 📖 Project Overview

MachineDoc is an AI service that instantly retrieves the relevant manual via RAG when an equipment error code occurs on the factory floor, and automatically guides operators through diagnosis and corrective procedures by analyzing virtual sensor logs.

### Core Value

- 🔍 Manual search time reduced from 5–15 minutes → instant (within 10 seconds)
- 👷 Standardized action guides immediately available even for unskilled workers
- 📚 RAG-based source citation to prevent hallucination

---

## 🎯 Key Features

| Feature | Description |
|---|---|
| Error Code Search | Enter an error code → instantly retrieve relevant manual pages |
| Equipment Manual Lookup | Search manuals by equipment name or category |
| Anomaly Detection Demo | Input virtual logs → LLM analysis → estimate anomaly and root cause |
| Corrective Procedure Guide | Step-by-step corrective actions via RAG + LLM summarization |
| Manual Management | Upload PDF → automatic chunking & embedding (admin only) |

---

## 📂 Repository Structure

```
.
├── frontend/        # React 18 + Vite + TypeScript (port 5173)
├── backend/         # FastAPI + SQLAlchemy + JWT (port 8000)
├── ai-service/      # FastAPI + LangChain + custom hybrid RAG (port 8001)
├── docker-compose.yml
├── shared/          # Environment variable templates, etc.
└── docs/            # Planning, design, architecture, presentation docs
```

`ai-service/README.md` covers the AI module's internal design in detail. Backend and frontend setup are documented in the **Quick Start** section below.

---

## 👥 Team

| Role | Owner |
|---|---|
| Frontend | Member A |
| Backend | Member B |
| AI · ML | Member C |

---

## 📅 Development Schedule

| Phase | Period | Key Deliverables |
|---|---|---|
| Phase 1 — Planning & Design | Apr 26 – Apr 29 | PRD, WBS, Wireframes, API Spec |
| Phase 2 — MVP Development | Apr 30 – May 4 | FE screens, BE APIs, AI RAG standalone |
| Phase 3 — AI Integration & Enhancement | May 5 – May 9 | Integration + anomaly detection + 80%+ accuracy |
| Phase 4 — QA & Demo Preparation | May 10 – May 13 | Testing, presentation materials, demo |

---

## 🛠️ Tech Stack

| Layer | Stack |
|---|---|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| Backend | FastAPI, Python 3.13, SQLAlchemy, JWT |
| AI/ML | LangChain (provider SDK only), OpenAI API (production), Ollama `qwen2.5:3b` + `nomic-embed-text` (local dev), bge-reranker-base, custom hybrid RAG |
| Database | PostgreSQL 15 + pgvector (HNSW) |
| DevOps | GitHub Actions, Docker Compose |

---

## ⚙️ Prerequisites

| Tool | Version | Install |
|---|---|---|
| **Git** | 2.40+ | https://git-scm.com/downloads |
| **Docker Desktop** | 4.x | https://www.docker.com/products/docker-desktop — runs Postgres+pgvector container |
| **Node.js** | 18+ (20 LTS recommended) | https://nodejs.org — frontend |
| **Python** | **3.10 to 3.12** (not 3.13) | https://www.python.org/downloads/ — backend works on 3.13 too, ai-service requires `>=3.10,<3.13` |
| **uv** (ai-service package manager) | latest | https://docs.astral.sh/uv/getting-started/installation/ — `pip install uv` or `winget install astral-sh.uv` |
| **Ollama** (local LLM runtime) | 0.3+ | https://ollama.com/download — local dev LLM/embedding |

> Postgres + pgvector run as a Docker container, no host install needed.
> For demo / production you can swap to OpenAI by setting `LLM_PROVIDER=openai` in `ai-service/.env`.

---

## 🚀 Quick Start (local dev)

### 0. Clone + env files

```bash
git clone <repo-url> MachineDoc
cd MachineDoc

# Root .env (consumed by docker-compose)
cat > .env <<'EOF'
DB_USER=ax_user
DB_PASSWORD=9ASs4xPr0j3Ct
DB_NAME=smart_factory
DB_HOST=db
DB_PORT=5433
DATABASE_URL=postgresql://ax_user:9ASs4xPr0j3Ct@db:5432/smart_factory
EOF
```

Create `backend/.env` and `ai-service/.env` using the templates below (no `.env.example` shipped):

```env
# backend/.env
DATABASE_URL=postgresql://ax_user:9ASs4xPr0j3Ct@localhost:5433/smart_factory
SECRET_KEY=dev-only-secret-key-do-not-use-in-prod-32bytes-min
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
APP_ENV=development
AI_SERVICE_URL=http://localhost:8001
# Manual PDFs are stored in ai-service/manuals (shared with ai-service for ingest).
# Backend auto-detects when unset, but pin it explicitly for stable deploys.
MANUAL_DIR=../ai-service/manuals

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

```env
# frontend/.env (Vite reads only VITE_-prefixed vars)
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws/v1
```

> Vite loads `.env` only at dev-server startup — restart `npm run dev` after editing.
> `VITE_API_BASE_URL` must include the `/api/v1` prefix (backend mounts every router under it); `VITE_WS_URL` must include `/ws/v1` (WebSocket router prefix).

### 1. Start Postgres + pgvector

```bash
docker compose up -d db
# Host 5433 maps to container 5432 (avoids local Postgres conflicts)
```

### 2. Apply migrations + seed

```bash
# 1) Schema is auto-created by SQLAlchemy `Base.metadata.create_all` on first backend boot.
# 2) Then apply incremental migrations:
docker exec -i smart_factory_db psql -U ax_user -d smart_factory < backend/migrations/001_init_prompts.sql
docker exec -i smart_factory_db psql -U ax_user -d smart_factory < backend/migrations/002_add_saved_manual_equipment_id.sql
docker exec -i smart_factory_db psql -U ax_user -d smart_factory < backend/migrations/003_rename_notification_occured_at.sql

# 3) Demo seed (5 equipment + 5 manuals + 25 demo error codes + 24h logs/notifications)
docker exec -i smart_factory_db psql -U ax_user -d smart_factory < backend/seeds/demo.sql
```

### 3. Pre-pull Ollama models (local dev)

```bash
ollama serve &              # port 11434
ollama pull qwen2.5:3b      # LLM (~2GB)
ollama pull nomic-embed-text  # embedding (~274MB)
```

### 4. Start each service

Open three terminals — local dev with hot reload.

#### 4-1. backend (port 8000)

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate          # Windows (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
uvicorn app.main:app --port 8000 --reload --workers 1
```

> **--workers 1 is required**: WebSocket broadcast uses an in-process `ConnectionManager`, so a multi-worker setup can't broadcast to connections held by other workers.

#### 4-2. ai-service (port 8001)

```bash
cd ai-service
uv sync                          # creates venv + installs deps automatically
uv run uvicorn app.main:app --host 0.0.0.0 --port 8001
```

> Two startup hooks fire on boot: `_warmup_embedder` (pages the Ollama embedding model into memory) and `_warmup_retrieval` (builds the RAG pipeline + runs a dummy retrieval to avoid cold-start 503s). First boot takes 30–60 seconds.

#### 4-3. frontend (port 5173)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

### 5. Index PDF manuals (optional)

The 8 PDFs in `ai-service/manuals/` need to be pre-indexed for RAG to return results. If you applied the demo seed, the index is already populated — otherwise upload through the admin manual-registration UI (`POST /api/v1/manual/upload` via backend, which forwards to ai-service `/ingest`) or the bulk-ingest script described in `ai-service/README.md`.

> Backend keeps each upload's **original filename** (e.g. `ga700.pdf`) for `saved_manual.file_url`; ai-service mirrors it in `manual_chunks_v2.source_file`. The two columns must stay in sync for citation→PDF resolution to work. After every successful ingest the ai-service automatically clears its filename + retrieval caches so new manuals are immediately searchable.

---

## 🐳 Docker Compose all-in-one (alternative)

To skip installing Python/Node on your host:

```bash
docker compose up -d
```

> Note: `frontend` is **not** defined in `docker-compose.yml` — run `npm run dev` on the host. Ollama also runs on the host; compose containers reach it via `host.docker.internal:11434`.

---

## 🧪 Smoke Test

| Target | Command | Expected |
|---|---|---|
| ai-service health | `curl http://localhost:8001/health` | `{"status":"ok"}` |
| ai-service RAG | `curl -X POST http://localhost:8001/api/v1/search -H "Content-Type: application/json" -d '{"error_code":"E5"}'` | `status:success` + ga700.pdf citation |
| backend docs | http://localhost:8000/docs | Swagger UI |
| frontend | http://localhost:5173 | login screen |

The 25 demo error codes used during the presentation are listed in `ai-service/.claude/planning/demo_error_codes_25.md` (gitignored, presenter-only).

---

## 📄 License

This project is a prototype built for portfolio purposes.

---


