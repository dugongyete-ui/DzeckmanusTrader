# AGENTS.md

> Canonical guide for AI coding agents working on the **AI Dzeck** codebase.

---

## Project Overview

**AI Dzeck** is an autonomous AI trading analyst platform. Users chat with an agent that analyzes financial markets (Forex, Crypto, Stocks) in real-time using MCP-connected data sources. The agent operates with **full autonomous reasoning** — it reads the market as a professional trader would, decides for itself which tools and parameters to use, and builds its analysis organically from what the data tells it. There are no hardcoded indicator sequences, no prescribed regime rules, and no fixed parameter defaults. Every analysis is unique to the current market state.

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
│   ├── economic-calendar/ # Real-time economic calendar (TradingView Calendar API)
│   ├── mongodb/       # MongoDB Atlas query tools
│   └── redis/         # Redis Cloud monitor tools
├── mcp.json           # MCP server definitions
├── .env.example       # Environment variable template
└── replit.md          # Replit project overview and user preferences
```

---

## Agent Architecture

### Orchestration Loop

The agent uses a **Plan → Execute → Update** loop (`backend/app/domain/services/flows/plan_act.py`):

1. **Planner** (`prompts/planner.py`) — decides how many steps are needed and describes the *goal* of each step, not the tools to use
2. **Execution agent** (`prompts/execution.py`) — reads the market, reasons about what it needs to know, chooses tools and parameters autonomously, interprets results in context
3. **Plan updater** — revises remaining steps based on what was actually found (e.g. extreme volatility reshapes the next steps)
4. **Summarizer** — delivers the final decision to the user
5. Results stream to frontend via **SSE**

### Autonomous Reasoning Model

The agent does **not** follow a fixed protocol or indicator checklist. It operates like a professional trader with full market awareness:

```
1. READ   — look at the current market state (price, session, volatility, direction)
2. THINK  — "what do I still need to understand before I can make a decision?"
3. CHOOSE — select the tool that best answers that question; set parameters based on
            what the current market conditions call for, not defaults
4. INTERPRET — synthesize the result with everything already known
5. REPEAT — until enough conviction exists to decide, or until TUNGGU is clearly right
```

Before calling any tool, the agent states **why** it needs it.
After reading a result, the agent states **what it means** in context — not just the raw numbers.

**Notification protocol (mandatory):** The agent MUST call `message-notify-user` before AND after every tool call. Before: what it is about to check and why. After: what it found and what it means. These narrations appear as live text inside step cards in the frontend — not templates, but the agent's own words as it thinks.

This means:
- No two analyses are identical, even for the same asset
- The agent may call RSI(9) one day and RSI(21) the next — based on current volatility
- The agent may use Ichimoku on a trending day and skip it entirely on a ranging day
- The agent narrates its thinking live at every tool call, making the analysis transparent and conversational

### Active Toolkits

| Toolkit | Tools | Purpose |
|---|---|---|
| **MCP toolkit** | All tools from `mcp.json` | Market data, indicators, DB persistence, time/session |
| **Search toolkit** | `info-search-web` | Economic calendar, news, fundamental events via Tavily |
| **Message toolkit** | `message-notify-user`, `message-ask-user` | Live progress updates + user clarification |

### MCP Servers (`mcp.json`)

| Server | Key Tools | Instruments |
|---|---|---|
| `time` | `forex-market-hours`, `get-current-time`, `convert-timezone` | All — session/time checks |
| `deriv` | `deriv-smart-analysis`, `deriv-rsi`, `deriv-macd`, `deriv-bbands`, `deriv-ema`, `deriv-atr`, `deriv-stoch`, `deriv-technical-analysis`, `deriv-ichimoku`, `deriv-supertrend`, `deriv-fibonacci`, `deriv-pivot-points`, `deriv-cci`, `deriv-williams-r`, `deriv-heikin-ashi`, `deriv-keltner`, `deriv-donchian`, `deriv-parabolic-sar` | XAUUSD, frxEURUSD, frxGBPUSD, all Deriv Forex |
| `tradingview` | `coin_analysis`, `multi_timeframe_analysis`, `advanced_candle_pattern`, `volume_confirmation_analysis`, `bollinger_scan`, `backtest_strategy` | BTC, ETH, all crypto, stocks, indices |
| `economic-calendar` | `calendar-today`, `calendar-upcoming`, `calendar-find-event`, `calendar-get-week` | All — fundamental event queries |
| `sentiment` | `sentiment-ls-ratio`, `sentiment-top-traders`, `sentiment-open-interest`, `sentiment-fear-greed` | Crypto only — Binance Futures pairs (BTCUSDT, ETHUSDT, etc.) |
| `mongodb` | find, aggregate, count | Signal storage and history |
| `redis` | get/set, stats | Real-time data cache |

### Tool Routing Rule

This is a **technical constraint**, not a strategy rule — it reflects what each data source actually provides:

```
Deriv MCP   → ONLY for Deriv platform instruments: frxXAUUSD, frxEURUSD, frxGBPUSD, frxXAGUSD, etc.
TradingView → Everything else: BINANCE:BTCUSDT, NASDAQ:AAPL, SP:SPX, etc.
Sentiment   → ONLY for crypto Binance Futures pairs: BTCUSDT, ETHUSDT, SOLUSDT, etc.
             NOT applicable to Forex or Gold.
```

### Prompt Files (source of agent behavior)

| File | Role |
|---|---|
| `prompts/system.py` | Agent identity + tool catalog (what each tool measures) + tool routing + decision format + security rules |
| `prompts/planner.py` | Goal-oriented planning — describes *what* to understand, not *which tools* to call. Step count varies by complexity. |
| `prompts/execution.py` | Reasoning-first execution — agent MUST call `message-notify-user` before AND after every tool call; explains why before each call and what the result means after; all parameters chosen autonomously |

#### How to modify agent behavior

- To change **what the agent is** and what tools it knows about → edit `system.py`
- To change **how plans are structured** (step granularity, how goals are described) → edit `planner.py`
- To change **how the agent reasons** during execution (notification cadence, parameter logic, decision format) → edit `execution.py`
- **Always restart the Backend API workflow** after any prompt change

#### Notification rendering (frontend)

`message-notify-user` tool events render as **text prose** inside step cards via `ToolUse.vue`:
- `tool.name === 'message' && tool.args?.text` → rendered as markdown text (no chip)
- All other tools → rendered as a clickable chip with status indicator
- The live narration appears between tool chips as the agent works through each step

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
4. Create a session, send: `"Carikan entry XAUUSD sekarang"`
5. Observe in backend logs that the agent reasons through its tool choices organically
6. The agent should explain *why* it calls each tool before calling it
7. Check backend logs in the **Backend API** workflow console

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

### Adding a New MCP Server

1. Add the server script to `mcp-servers/<name>/server.py`
2. Register it in `mcp.json` with `"enabled": true`
3. Add the server and its tools to the `<tool_catalog>` in `system.py` — describe what each tool **measures** and what **question** it answers
4. Add tool routing rules in `system.py` under `<tool_routing>` if the server has platform-specific instruments
5. Restart **Backend API**

> Do NOT add prescriptive rules about when to use the new tools. The catalog description is enough — the agent will decide when to use them based on its own reasoning.

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

Look for these log patterns to trace agent execution:
```
"Agent started processing message"   → planner triggered
"created plan with N steps"          → plan created (varies by request complexity)
"executing step 1"                   → first step running (market read)
"executing step 2"                   → deeper analysis running
"executing step 3"                   → decision delivery (if 3-step plan)
"state changed ... to COMPLETED"     → analysis finished
```

In the execution output, healthy autonomous reasoning looks like:
```
"Saya ingin tahu seberapa kuat tren ini — saya panggil deriv-atr dulu untuk ukur volatilitas"
"ATR = 1.82, rata-rata sekitar 1.45 — volatilitas sedikit di atas normal tapi masih aman"
"Karena ada arah yang jelas, saya perlu check struktur besar — pilih Ichimoku H4"
```

### Frontend Logs
Check the **Start application** workflow console, or the browser DevTools console.

### Common Issues

| Issue | Likely Cause | Fix |
|---|---|---|
| Agent calls tools without explaining why | Old prompt cache | Restart Backend API workflow |
| MCP tool returns empty / error | MCP server not running or wrong symbol format | Check `mcp.json`, verify symbol routing (Deriv vs TradingView) |
| Agent always says TUNGGU | Genuine market uncertainty or conflicting signals — this is correct behavior | Check ATR/volatility in logs; may be a real market condition |
| TradingView tools fail | `TV_PROXY_BASE` misconfigured or scanner.tradingview.com blocked | Set/check `TV_PROXY_BASE` env var |

### Resetting State

- MongoDB data is in Atlas cloud — wipe via Atlas console if needed.
- Redis data is in Redis Cloud — flush via Redis Cloud console if needed.
