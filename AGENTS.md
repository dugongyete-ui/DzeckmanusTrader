# AGENTS.md

> Canonical guide for AI coding agents working on the **AI Dzeck** codebase.

---

## Project Overview

**AI Dzeck** is an autonomous AI trading analyst platform. Users chat with an agent that analyzes financial markets (Forex, Crypto, Stocks) in real-time using MCP-connected data sources. The agent is **market-aware and adaptive** — it scans current market conditions first, diagnoses the market regime, then self-configures its indicator set before delivering a decision. Analysis streams live to the frontend.

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
│       │       ├── prompts/  # System, planner, execution prompts ← core agent logic
│       │       └── toolkits/ # Tool registries (MCP, search, message)
│       ├── application/      # Application services (auth, agent, file, token, email)
│       ├── infrastructure/   # External integrations (DB, cache, search, MCP)
│       ├── interfaces/       # API routes, schemas, error handlers, dependencies
│       ├── core/             # Config (config.py)
│       └── main.py
├── mcp-servers/       # Local MCP server implementations
│   ├── deriv/         # Deriv platform — Forex/Gold indicators & analysis
│   ├── tradingview/   # TradingView wrapper — Crypto/Stocks (uses tradingview-mcp package)
│   ├── time/          # Time & forex market session tools
│   ├── mongodb/       # MongoDB Atlas query tools
│   └── redis/         # Redis Cloud monitor tools
├── mcp.json           # MCP server definitions (time, mongodb, redis, deriv, tradingview)
├── .env.example       # Environment variable template
└── replit.md          # Replit project overview and user preferences
```

---

## Agent Architecture

### Orchestration Loop

The agent uses a **Plan → Execute → Update** loop (`backend/app/domain/services/flows/plan_act.py`):

1. **Planner** (`prompts/planner.py`) — creates a step-by-step plan structured around the 4-phase adaptive protocol
2. **Execution agent** (`prompts/execution.py`) — runs each step, calls tools, interprets results
3. **Plan updater** — revises remaining steps based on what the execution found (e.g. regime changes the next tool selection)
4. **Summarizer** — delivers the final structured decision to the user
5. Results stream to frontend via **SSE**

### Adaptive Analysis Protocol (4 Phases)

Every market analysis request mandatorily goes through four phases. This is enforced in all three prompt files.

```
Phase 0 — SCAN
  Read raw market state: session activity, current price, ATR (volatility), ADX (trend strength)
  Tools: forex-market-hours → deriv-market-snapshot → deriv-atr → deriv-technical-analysis
         (or coin_analysis for TradingView assets)

Phase 1 — DIAGNOSE
  Classify market into one of four regimes based on scan data:
  ┌─────────────────────────────────────────────────────────────────┐
  │ Regime A — Strong Trend    : ADX > 25, clear directional move  │
  │ Regime B — Weak/Transition : ADX 20-25, mixed signals          │
  │ Regime C — Ranging         : ADX < 20, price bouncing S/R      │
  │ Regime D — Volatility Spike: ATR > 150% of average → NO ENTRY  │
  └─────────────────────────────────────────────────────────────────┘

Phase 2 — SELF-CONFIGURE
  Choose indicator set and parameters appropriate for the diagnosed regime:
  Regime A → trend-following  : deriv-smart-analysis + deriv-macd + deriv-ema(50/200)
  Regime B → confirmation     : deriv-smart-analysis + deriv-rsi + deriv-bbands
  Regime C → mean-reversion   : deriv-stoch + deriv-rsi + deriv-bbands + S/R levels
  Regime D → standby          : notify user, do NOT run entry analysis

Phase 3 — DECIDE
  Synthesize results into a structured decision:
  Regime → Key signals → BUY/SELL/TUNGGU → Entry / SL (ATR-based) / TP1 / TP2 / Risk %
```

### Active Toolkits

| Toolkit | Tools | Purpose |
|---|---|---|
| **MCP toolkit** | All tools from `mcp.json` | Market data, indicators, DB persistence, time/session |
| **Search toolkit** | `info-search-web` | Economic calendar, news, fundamental events via Tavily |
| **Message toolkit** | `message-notify-user`, `message-ask-user` | Live progress updates + user clarification |

### MCP Servers (`mcp.json`)

| Server | Key Tools | Instruments |
|---|---|---|
| `time` | `forex-market-hours` | All — session/time checks |
| `deriv` | `deriv-smart-analysis`, `deriv-rsi`, `deriv-macd`, `deriv-bbands`, `deriv-ema`, `deriv-atr`, `deriv-stoch`, `deriv-technical-analysis` | XAUUSD, frxEURUSD, frxGBPUSD, all Deriv Forex |
| `tradingview` | `coin_analysis`, `multi_timeframe_analysis`, `advanced_candle_pattern`, `volume_breakout_scanner`, `bollinger_scan`, `backtest_strategy` | BTC, ETH, all crypto, stocks, indices |
| `mongodb` | find, aggregate, count | Signal storage and history |
| `redis` | get/set, stats | Real-time data cache |

### Tool Routing Rule

```
Deriv MCP  → ONLY for Deriv platform: frxXAUUSD, frxEURUSD, frxGBPUSD, frxXAGUSD, etc.
TradingView → Everything else: BINANCE:BTCUSDT, NASDAQ:AAPL, SP:SPX, etc.
```

### Prompt Files (source of agent behavior)

| File | Role |
|---|---|
| `prompts/system.py` | Agent identity + full adaptive protocol definition + regime rules + confidence thresholds |
| `prompts/planner.py` | Plan creation rules — always generates 3-step scan→configure→decide structure for analysis |
| `prompts/execution.py` | Step execution rules — which tools to call per regime, notification cadence, decision format |

---

## Development Environment (Replit)

### Running Services

Two workflows run in parallel:

| Workflow | Command | Port |
|---|---|---|
| **Start application** | `cd frontend && pnpm dev` | 5000 |
| **Backend API** | `cd backend && python3 -m uvicorn app.main:app --host localhost --port 8000` | 8000 |

To restart a workflow, use the Replit workflow UI or the `restart_workflow` agent tool.

> **Important:** After editing any file in `backend/app/domain/services/prompts/`, restart the **Backend API** workflow for changes to take effect.

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
| `TV_PROXY_BASE` | Optional proxy for TradingView scanner requests |

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
4. Create a session, send: `"Analisa XAUUSD sekarang"`
5. Verify the agent goes through Scan → Diagnose → Configure → Decide phases in the backend logs
6. Check backend logs in the **Backend API** workflow console

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

### Modifying Agent Behavior

All agent behavior is controlled via the three prompt files in `backend/app/domain/services/prompts/`:
- To change how the agent thinks → edit `system.py`
- To change how plans are structured → edit `planner.py`
- To change how steps are executed → edit `execution.py`
- Always restart the **Backend API** workflow after prompt changes

### Adding a New MCP Server

1. Add the server script to `mcp-servers/<name>/server.py`
2. Register it in `mcp.json` with `"enabled": true`
3. Add tool routing rules in `system.py` under `<tool_routing>`
4. Add relevant execution rules in `execution.py` for the new tool set
5. Restart **Backend API**

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

Look for these log patterns to trace the adaptive protocol:
```
"Agent started processing message"   → planner triggered
"created plan with N steps"          → plan created (should be 3 steps for analysis)
"executing step 1"                   → Phase 0 scan running
"executing step 2"                   → Phase 1+2 diagnose & configure running
"executing step 3"                   → Phase 3 decision delivery
"state changed ... to COMPLETED"     → analysis finished
```

### Frontend Logs
Check the **Start application** workflow console, or the browser DevTools console.

### Common Issues

| Issue | Likely Cause | Fix |
|---|---|---|
| Agent jumps straight to decision without scanning | Prompt cache from old version | Restart Backend API workflow |
| MCP tool returns empty / error | MCP server not running or wrong symbol format | Check `mcp.json`, verify symbol routing (Deriv vs TradingView) |
| Agent always says TUNGGU | Confluence consistently < 58% | Check ATR/ADX values in logs — may be a market condition, not a bug |
| TradingView tools fail | `TV_PROXY_BASE` misconfigured or scanner.tradingview.com blocked | Set/check `TV_PROXY_BASE` env var |

### Resetting State

- MongoDB data is in Atlas cloud — wipe via Atlas console if needed.
- Redis data is in Redis Cloud — flush via Redis Cloud console if needed.
