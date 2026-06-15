# AI Dzeck

Autonomous AI trading analyst platform built with FastAPI + Vue 3. Users chat with an AI agent that analyzes financial markets (Forex, Crypto, Stocks) in real-time. The agent is **market-aware and adaptive** — it scans market conditions first, diagnoses the regime, self-configures its indicator set, then delivers a structured trading decision. All analysis streams live to the frontend.

## Architecture

| Service | Stack | Port | Entry Point |
|---|---|---|---|
| **Frontend** | Vue 3 + TypeScript + Vite + Tailwind | 5000 | `frontend/src/main.ts` |
| **Backend** | Python 3.12, FastAPI, LangChain, Beanie | 8000 | `backend/app/main.py` |

**Database:** MongoDB Atlas (cloud) + Redis Cloud (Asia Southeast)

## Adaptive Analysis Protocol

Every market analysis goes through 4 mandatory phases:

| Phase | What happens |
|---|---|
| **0 — Scan** | Session check, economic calendar risk check, price snapshot, ATR (volatility), ADX (trend strength) |
| **1 — Diagnose** | Classify market regime: A (strong trend), B (transition), C (ranging), D (volatility spike) |
| **2 — Configure** | Self-select indicators for the regime — trend tools for A, oscillators for C, standby for D |
| **3 — Decide** | Deliver BUY/SELL/TUNGGU with Entry, SL (ATR-based), TP1, TP2, confidence, risk % |

## MCP Servers (6 servers — 72 tools total)

All servers defined in `mcp.json`, launched as stdio subprocesses.

| Server | Tools | Purpose |
|---|---|---|
| **time** | 4 | Session clock, forex market hours (London/NY/Tokyo/Sydney), timezone conversion |
| **mongodb** | 5 | MongoDB Atlas monitoring — find, count, aggregate, stats |
| **redis** | 6 | Redis Cloud monitoring — keys, values, stats, flush |
| **deriv** | 24 | Deriv platform: Gold (frxXAUUSD), Forex pairs — price, candles, RSI, MACD, BB, EMA, ATR, Stoch, Ichimoku, Supertrend, Fibonacci, Pivots, Heikin-Ashi, Smart Analysis, etc. |
| **tradingview** | 29 | Crypto/Stocks/Indices — screener, multi-timeframe analysis, volume confirmation, backtesting, market sentiment, Yahoo Finance news (proxy via `TV_PROXY_BASE`) |
| **economic-calendar** | 4 | Real-time economic calendar: CPI, FOMC, NFP, GDP, PMI, all central bank decisions — with forecast/actual/previous and WIB countdown. Source: TradingView Calendar API (60-min disk cache at `/tmp/ecocal_cache.json`) |

### Economic Calendar Tools
- `calendar-today` — all events releasing today with impact level and actual values
- `calendar-upcoming` — next N high-impact events from now with countdown timer (called in every Phase 0 scan)
- `calendar-find-event` — find specific event: FOMC, BOJ, CPI, NFP, GDP, PMI, BOE, RBA, etc.
- `calendar-get-week` — full calendar for next 3 weeks grouped by day

### Tool Routing Rules
- **Deriv MCP** → `frxXAUUSD`, `frxEURUSD`, `frxGBPUSD`, `frxUSDJPY`, all `frx*` pairs
- **TradingView MCP** → `BINANCE:BTCUSDT`, `BINANCE:ETHUSDT`, `NASDAQ:AAPL`, `SP:SPX`, all crypto/stocks/indices
- **Economic Calendar MCP** → all fundamental queries: "kapan CPI?", "ada event hari ini?", news risk check before entry

## Agent Toolkits

- **MCP toolkit** — 6 servers, 72 tools (data, indicators, calendar, DB monitoring)
- **Search toolkit** — Web search via Tavily for real-time news and in-depth research
- **Message toolkit** — `message-notify-user` (live progress), `message-ask-user` (clarification)

## Core Prompt Files

All agent behavior is controlled by three files in `backend/app/domain/services/prompts/`:

| File | Role |
|---|---|
| `system.py` | Agent identity, tool routing rules, adaptive protocol phases, regime classification, economic calendar guide, security rules |
| `planner.py` | Plan structure — always: scan → diagnose+configure → decide. Handles multi-asset, file attachments, conversational vs analysis routing |
| `execution.py` | Per-phase execution logic: Phase 0 scan order, Regime A/B/C/D indicator selection with adaptive parameters, decision format (Entry/SL/TP/Confidence), TUNGGU conditions |

After editing any prompt file, restart the **Backend API** workflow.

### Market Regimes
| Regime | Condition | Indicator Set |
|---|---|---|
| **A** | ADX > 25 (strong trend) | Smart Analysis, Ichimoku, Supertrend, MACD, EMA(21/50/200), Fibonacci, Pivots, Heikin-Ashi |
| **B** | ADX 20–25 (transition) | Smart Analysis, RSI(14), BB, Williams%R, Pivots, optional Heikin-Ashi |
| **C** | ADX < 20 (ranging) | Stoch(5), RSI(9), CCI, Williams%R, BB, Technical Analysis, Pivots, Heikin-Ashi |
| **D** | ATR spike > 150% avg | STOP — no entry, notify user, wait for ATR to normalize |

## Frontend Pages & Components

**Pages** (`frontend/src/pages/`):
- `LandingPage.vue` — product landing
- `LoginPage.vue` — JWT auth
- `ChatPage.vue` — main analysis workspace
- `SharePage.vue` / `ShareLayout.vue` — view shared sessions

**Key Components** (`frontend/src/components/`):
- `ChatBox.vue` / `ChatMessage.vue` — conversation interface
- `PlanPanel.vue` — real-time step-by-step plan visualization
- `ToolPanel.vue` / `ToolUse.vue` / `ToolPanelContent.vue` — tool call display with formatted output
- `LeftPanel.vue` — session navigation
- `FilePanel.vue` / `FilePanelContent.vue` — uploaded file management

## Running on Replit

Two primary workflows:
- **Start application** — Vite dev server on port 5000, proxies `/api` → backend
- **Backend API** — FastAPI + Uvicorn on port 8000

Validation workflows (run on-demand):
- `backend-syntax` — AST parse all Python files
- `backend-imports` — import all key modules
- `backend-pytest` — run test suite
- `frontend-typecheck` — `vue-tsc --noEmit`

## Key Environment Variables

All configured in Replit Secrets:
- `API_KEY` / `API_BASE` — LLM provider credentials
- `MODEL_NAME` — currently `qwen3.7-max`
- `VISION_MODEL_NAME` — `qwen2.5-vl-72b-instruct` (for chart image analysis)
- `MONGODB_URI` — MongoDB Atlas connection string
- `REDIS_HOST` / `REDIS_PORT` / `REDIS_PASSWORD` — Redis Cloud (Asia Southeast)
- `TAVILY_API_KEY` — web search
- `AUTH_PROVIDER` — `password` (JWT-based auth)
- `SEARCH_PROVIDER` — `tavily`
- `TV_PROXY_BASE` — TradingView screener proxy URL (avoids geo-blocking)

## User Preferences

- API keys stay in Replit Secrets (personal project)
- No Docker — all services run directly in the Replit container
- MongoDB Atlas + Redis Cloud for persistence (no local DB)
- Both English and Chinese documentation must be kept in sync when updating docs
