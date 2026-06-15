# AI Dzeck

Autonomous AI trading analyst platform built with FastAPI + Vue 3. Users chat with an AI agent that analyzes financial markets (Forex, Crypto, Stocks) in real-time. The agent operates with **full autonomous reasoning** — like a professional trader given consciousness. It reads the market from scratch, decides for itself which tools and parameters to use, and builds its analysis organically from what the data tells it. No hardcoded indicator sequences. No prescribed rules. Every analysis is a fresh, adaptive response to current market conditions.

## Architecture

| Service | Stack | Port | Entry Point |
|---|---|---|---|
| **Frontend** | Vue 3 + TypeScript + Vite + Tailwind | 5000 | `frontend/src/main.ts` |
| **Backend** | Python 3.12, FastAPI, LangChain, Beanie | 8000 | `backend/app/main.py` |

**Database:** MongoDB Atlas (cloud) + Redis Cloud (Asia Southeast)

## How the Agent Thinks

The agent does not follow a checklist. It reasons like a professional trader:

1. **Read** — understand the current market state (price, session, volatility, trend)
2. **Think** — "what do I still need to know before I can make a decision?"
3. **Choose** — pick the tool that answers that question; set parameters based on current conditions
4. **Interpret** — synthesize the result with everything already known
5. **Repeat** — until there is enough conviction to decide, or until TUNGGU is clearly right

Before calling any tool, the agent explains **why** it needs it.
After reading a result, the agent explains **what it means** in context.

**Notification protocol (mandatory):** The agent MUST call `message-notify-user` before AND after every tool call. These live narrations appear as text inside step cards — the agent's own words as it thinks aloud, not templates. Do not add example strings or hardcoded phrasing to the notification prompt — the agent must speak in its own voice.

This means the agent may use RSI(9) one session and RSI(21) the next — based on what the market demands. It may use Ichimoku on a trending day and skip it entirely on a ranging day. No two analyses are identical.

## MCP Servers (7 servers — ~76 tools total)

All servers defined in `mcp.json`, launched as stdio subprocesses.

| Server | Tools | Purpose |
|---|---|---|
| **time** | 4 | Session clock, forex market hours (London/NY/Tokyo/Sydney), timezone conversion |
| **mongodb** | 5 | MongoDB Atlas monitoring — find, count, aggregate, stats |
| **redis** | 6 | Redis Cloud monitoring — keys, values, stats, flush |
| **deriv** | 24 | Deriv platform: Gold (frxXAUUSD), Forex pairs — price, candles, RSI, MACD, BB, EMA, ATR, Stoch, Ichimoku, Supertrend, Fibonacci, Pivots, Heikin-Ashi, CCI, Williams%R, Keltner, Donchian, Parabolic SAR, Smart Analysis, etc. |
| **tradingview** | 29 | Crypto/Stocks/Indices — screener, multi-timeframe analysis, volume confirmation, backtesting, market sentiment (proxy via `TV_PROXY_BASE`) |
| **economic-calendar** | 4 | Real-time economic calendar: CPI, FOMC, NFP, GDP, PMI, all central bank decisions — with forecast/actual/previous and WIB countdown. Source: TradingView Calendar API (60-min disk cache at `/tmp/ecocal_cache.json`) |
| **sentiment** | 4 | Market sentiment for crypto: Long/Short Ratio, Top Trader Positioning, Open Interest, Fear & Greed Index. Data: Binance Futures API + Alternative.me. Free, no API key, real-time. |

### Economic Calendar Tools
- `calendar-today` — all events releasing today with impact level and actual values
- `calendar-upcoming` — next N high-impact events from now with countdown timer
- `calendar-find-event` — find specific event: FOMC, BOJ, CPI, NFP, GDP, PMI, BOE, RBA, etc.
- `calendar-get-week` — full calendar for next 3 weeks grouped by day

### Sentiment Tools (crypto only — Binance Futures pairs, free, no API key)
- `sentiment-ls-ratio` — % Long vs Short all traders right now; high Long% (>65%) = crowded long = potential sell signal
- `sentiment-top-traders` — positioning of institutional / smart money (top account holders on Binance Futures)
- `sentiment-open-interest` — trend of open interest: new money entering or exiting a move
- `sentiment-fear-greed` — overall crypto market sentiment index (0-100): Extreme Fear → contrarian buy; Extreme Greed → reversal risk

> **Limitation:** Sentiment tools only work for Binance Futures pairs (BTCUSDT, ETHUSDT, SOLUSDT, etc.). Not applicable to Forex or Gold.

### Tool Routing (Technical Constraint — Not a Strategy Rule)
- **Deriv MCP** → `frxXAUUSD`, `frxEURUSD`, `frxGBPUSD`, `frxUSDJPY`, all `frx*` pairs
- **TradingView MCP** → `BINANCE:BTCUSDT`, `BINANCE:ETHUSDT`, `NASDAQ:AAPL`, `SP:SPX`, all crypto/stocks/indices
- **Economic Calendar MCP** → all fundamental queries: "kapan CPI?", "ada event hari ini?", news risk check before entry
- **Sentiment MCP** → crypto Binance Futures pairs only (BTCUSDT, ETHUSDT, SOLUSDT, etc.) — NOT for Forex/Gold

## Agent Toolkits

- **MCP toolkit** — 7 servers, ~76 tools (data, indicators, sentiment, calendar, DB monitoring)
- **Search toolkit** — Web search via Tavily for real-time news and in-depth research
- **Message toolkit** — `message-notify-user` (live progress), `message-ask-user` (clarification)

## Core Prompt Files

All agent behavior is controlled by three files in `backend/app/domain/services/prompts/`:

| File | Role |
|---|---|
| `system.py` | Agent identity, tool catalog (what each tool measures and what question it answers), tool routing, decision output format, security rules |
| `planner.py` | Goal-oriented planning — describes *what* needs to be understood per step, not which tools to call. Step count determined by request complexity. |
| `execution.py` | Reasoning-first execution — agent explains why before each tool call, interprets results in context, sets all parameters autonomously based on current market state |

After editing any prompt file, restart the **Backend API** workflow.

## What Autonomous Means Here

The agent decides everything based on what it finds — no hardcoded rules:

| Aspect | How it works |
|---|---|
| **Which indicators to use** | Agent chooses based on what it needs to understand at that moment |
| **Which parameters to set** | Agent sets based on current volatility, timeframe, and market character |
| **How many tools to call** | Agent calls as many or as few as needed to reach conviction |
| **How to interpret results** | Agent synthesizes in context of everything it already knows |
| **When to say TUNGGU** | Agent judges honestly — conflicting signals, extreme volatility, imminent news |
| **Decision delivery** | Agent describes the market in its own words, not a regime label |

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

## Features

### File Upload & Extraction
Users dapat upload file (PDF, DOCX, PPTX, XLSX, CSV, TXT, gambar) langsung dari chat. Backend melakukan **server-side text extraction** tanpa sandbox — hasil teks langsung diinjeksi ke konteks agen sebagai `<file name="...">...</file>` sehingga agen bisa membaca isinya. Chart image diproses oleh vision model lalu dikonversi ke deskripsi teks sebelum diteruskan ke execution agent.

### Session Sharing
Setiap session bisa dibagikan publik via tombol "Share" di header chat. Session yang dibagikan bisa dilihat siapa saja lewat `/shared/{session_id}` tanpa login. Sharing bisa dicabut kapan saja.

### Admin User Management
User dengan `role = "admin"` di MongoDB bisa melihat, deactivate, dan activate user lain via API (`/auth/user/{id}/deactivate`, `/auth/user/{id}/activate`). Admin tidak bisa deactivate dirinya sendiri.

### Password Reset via Email
Jika SMTP dikonfigurasi (`EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USERNAME`, `EMAIL_PASSWORD`, `EMAIL_FROM`), user bisa reset password via 6-digit verification code yang dikirim ke email (TTL 5 menit, maks 3 percobaan).

### TradingView Tools Filter
Backend memfilter tools TradingView dari ~100+ ke **27 tools spesifik** yang relevan untuk trading signal. Filter ada di `backend/app/domain/services/tools/mcp.py` (`_TRADINGVIEW_ALLOWED`).

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

All configured in Replit Secrets / userenv:

**Required:**
- `API_KEY` / `API_BASE` / `MODEL_NAME` / `MODEL_PROVIDER` — LLM provider credentials
- `MONGODB_URI` / `MONGODB_DATABASE` — MongoDB Atlas
- `REDIS_HOST` / `REDIS_PORT` / `REDIS_PASSWORD` — Redis Cloud (Asia Southeast)
- `JWT_SECRET_KEY` / `PASSWORD_SALT` — auth security
- `AUTH_PROVIDER` — `password` (JWT-based auth)

**Vision & planning (optional):**
- `VISION_MODEL_NAME` / `VISION_API_BASE` / `VISION_API_KEY` — dedicated model for chart image analysis (`qwen2.5-vl-72b-instruct`)
- `PLANNER_MODEL_NAME` / `PLANNER_API_BASE` / `PLANNER_API_KEY` — separate model for the planning step (optional, uses main model if not set)
- `SUMMARY_MODEL_NAME` — model for auto-generating session titles

**Search & proxy:**
- `TAVILY_API_KEY` — web search
- `SEARCH_PROVIDER` — `tavily`
- `TV_PROXY_BASE` — TradingView screener proxy URL (avoids geo-blocking)
- `SSL_VERIFY` — set `false` for custom LLM gateways with self-signed TLS certs

**Advanced / optional:**
- `EXTEND_SYSTEM_MESSAGE` — extra instructions appended to all agent system prompts at runtime (no prompt file edit needed)
- `CONVERSATION_SAVE_PATH` — directory to save raw conversation logs to disk (e.g. `/tmp/conversations`)
- `EXTRA_HEADERS` — JSON object of extra HTTP headers for every LLM request
- `BROWSER_MAX_STEPS` — max tool calls before forced summarize (default: `100`)
- `EMAIL_HOST` / `EMAIL_PORT` / `EMAIL_USERNAME` / `EMAIL_PASSWORD` / `EMAIL_FROM` — SMTP config for password reset emails
- `GOOGLE_ANALYTICS_ID` — Google Analytics ID (sent to frontend at startup)

## User Preferences

- API keys stay in Replit Secrets (personal project)
- No Docker — all services run directly in the Replit container
- MongoDB Atlas + Redis Cloud for persistence (no local DB)
- Agent is reasoning-first and fully autonomous — do not add hardcoded indicator rules back to prompts
- Both English and Chinese documentation must be kept in sync when updating docs
