# AGENTS.md

> Canonical guide for AI coding agents working on the **AI Dzeck × Claw** codebase.

---

## Project Overview

**AI Dzeck** is an autonomous AI trading analyst platform. Users chat with an agent that analyzes financial markets (Forex, Crypto, Stocks) in real-time using MCP-connected data sources — Deriv for Forex/Gold and TradingView for Crypto/Stocks. Analysis is streamed live to the frontend.

| Service | Stack | Port (dev) | Entry Point |
|---|---|---|---|
| **Frontend** | Vue 3 + TypeScript, Vite 4, Tailwind CSS | 5000 | `frontend/src/main.ts` |
| **Backend** | Python 3.12, FastAPI, LangChain, Beanie/Motor | 8000 | `backend/app/main.py` |

Infrastructure: **MongoDB Atlas** (cloud), **Redis Cloud** (Asia Southeast). No local Docker required.

---

## Directory Structure

```
dzeck/
├── frontend/          # Vue 3 SPA (Vite, TypeScript, Tailwind)
│   └── src/
│       ├── api/              # HTTP + SSE clients (agent, auth, config, files)
│       ├── assets/           # Global CSS + theme
│       ├── components/       # UI components
│       │   ├── icons/        # SVG icon components
│       │   ├── settings/     # Settings dialog panels
│       │   ├── toolViews/    # Tool result renderers (SearchToolView, McpToolView)
│       │   └── ui/           # Generic UI primitives (dialog, context menu, etc.)
│       ├── composables/      # Vue composables (theme, i18n, left panel, etc.)
│       ├── constants/        # Tool mappings (tool.ts)
│       ├── pages/            # Route-level page components
│       ├── stores/           # Pinia stores
│       ├── types/            # TypeScript type definitions
│       └── utils/            # Helpers (toast, markdown, etc.)
├── backend/           # FastAPI backend (DDD layout)
│   └── app/
│       ├── domain/           # Models, services, tools, agents, repositories
│       │   └── services/
│       │       ├── agents/   # Planner + Execution agents (LangChain)
│       │       ├── flows/    # Plan-Act orchestration loop
│       │       ├── prompts/  # System, planner, execution prompts
│       │       └── toolkits/ # Tool registries (MCP, search, message)
│       ├── application/      # Application services (auth, agent, file, token, email)
│       ├── infrastructure/   # External integrations (DB, cache, search, MCP)
│       ├── interfaces/       # API routes, schemas, error handlers, dependencies
│       ├── core/             # Config (config.py)
│       └── main.py
├── mcp.json           # MCP server definitions (time, mongodb, redis, deriv, tradingview)
├── .env.example       # Environment variable template
└── replit.md          # Replit project overview and user preferences
```

---

## Agent Architecture

The agent uses a **Plan → Execute → Update** loop (`backend/app/domain/services/flows/plan_act.py`):

1. **Planner** creates a step-by-step plan for the user's request
2. **Execution agent** runs each step using the registered toolkits
3. **Plan updater** revises remaining steps based on tool results
4. Results stream to frontend via SSE

### Active Toolkits

| Toolkit | Tools | Purpose |
|---|---|---|
| **MCP toolkit** | All tools from `mcp.json` | Deriv/TradingView market data, MongoDB, Redis, time |
| **Search toolkit** | `info_search_web` | Web search via Tavily for news/fundamentals |
| **Message toolkit** | `message_notify_user`, `message_ask_user` | User notifications and clarification |

### MCP Servers (`mcp.json`)

| Server | Purpose |
|---|---|
| `time` | Current time / market session checks |
| `mongodb` | Persist/query trade signals and history |
| `redis` | Fast cache for real-time data |
| `deriv` | Forex & Gold market data + multi-timeframe analysis |
| `tradingview` | Crypto, Stocks, all other asset classes |

---

## Development Environment (Replit)

### Running Services

Two workflows run in parallel:

| Workflow | Command | Port |
|---|---|---|
| **Start application** | `cd frontend && pnpm dev` | 5000 |
| **Backend API** | `cd backend && python3 -m uvicorn app.main:app --host localhost --port 8000` | 8000 |

To restart a workflow, use the Replit workflow UI or the `restart_workflow` agent tool.

### Key Environment Variables (configured in Replit)

| Variable | Purpose |
|---|---|
| `API_KEY` | LLM API key |
| `API_BASE` | LLM API base URL |
| `MODEL_NAME` | `qwen3.7-max` |
| `VISION_MODEL_NAME` | `qwen2.5-vl-72b-instruct` |
| `MONGODB_URI` | MongoDB Atlas connection string |
| `REDIS_HOST` / `REDIS_PORT` / `REDIS_PASSWORD` | Redis Cloud credentials |
| `TAVILY_API_KEY` | Web search (Tavily) |
| `AUTH_PROVIDER` | `password` (JWT-based auth) |
| `SEARCH_PROVIDER` | `tavily` |

---

## Testing

### Backend Tests (pytest — integration-style)

Tests live in `backend/tests/` and hit a **running** backend at `http://localhost:8000`.

```bash
# Ensure backend is running first (Backend API workflow)
cd backend
python3 -m pytest                               # all tests
python3 -m pytest tests/test_auth_routes.py     # specific file
python3 -m pytest -m file_api                   # by marker
```

Key test files:
- `tests/test_auth_routes.py` — auth endpoints
- `tests/test_api_file.py` — file upload/download

Config: `backend/pytest.ini` (`asyncio_mode = auto`, markers: `file_api`).

### Frontend (No Automated Test Runner)

```bash
cd frontend
npx vue-tsc --noEmit   # type check
pnpm build             # production build (catches TS + template errors)
```

### Validation Workflows (Replit)

| Workflow | What it checks |
|---|---|
| `backend-syntax` | Python AST parse — all `.py` files compile |
| `backend-imports` | All domain modules import without error |
| `backend-pytest` | Integration tests (requires running backend) |
| `frontend-typecheck` | `vue-tsc --noEmit` |

### Full-Stack Integration Test

1. Ensure both workflows are running
2. Open the app preview (port 5000)
3. Register/login (or set `AUTH_PROVIDER=none`)
4. Create session, send a market analysis request (e.g. "Analisa XAUUSD sekarang")
5. Check backend logs in the **Backend API** workflow console

---

## Code Conventions

### Backend (Python)

- **DDD architecture**: `domain/` → `application/` → `infrastructure/` → `interfaces/`
- **FastAPI** with **Pydantic v2** models and settings
- **Beanie** ODM for MongoDB documents (`infrastructure/models/documents.py`)
- **Redis** for caching and message queues
- Dependency management: **uv** + `pyproject.toml` (PEP 621)
- No enforced linter/formatter (no Ruff, Black, or Flake8 configured)
- Async-first: use `async def` for route handlers and service methods

### Frontend (TypeScript / Vue)

- **Vue 3 Composition API** with `<script setup lang="ts">`
- **TypeScript** throughout
- **Tailwind CSS** for styling, **reka-ui** component library
- Path alias: `@/` → `src/`
- **vue-i18n** for internationalization (Chinese + English)
- Dependency management: **pnpm** + `package.json`
- No ESLint or Prettier configured

### Tool Views

Tool results rendered in the chat use two components:
- `SearchToolView.vue` — displays web search results
- `McpToolView.vue` — displays MCP tool call results (market data, signals, etc.)

Mappings from tool name → icon → component live in `frontend/src/constants/tool.ts`.

---

## Debugging

### Backend Logs
Check the **Backend API** workflow console in Replit, or read `/tmp/logs/Backend_API_*.log`.

### Frontend Logs
Check the **Start application** workflow console, or the browser DevTools console.

### Resetting State

- MongoDB data is in Atlas cloud — wipe via Atlas console if needed.
- Redis data is in Redis Cloud — flush via Redis Cloud console if needed.
