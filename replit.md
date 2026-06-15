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
| **0 — Scan** | Read session, price, ATR (volatility), ADX (trend strength) |
| **1 — Diagnose** | Classify market regime: A (strong trend), B (transition), C (ranging), D (volatility spike) |
| **2 — Configure** | Self-select indicators appropriate for the regime — trend tools for A, oscillators for C, standby for D |
| **3 — Decide** | Deliver BUY/SELL/TUNGGU with Entry, SL (ATR-based), TP1, TP2, confidence, risk % |

## Agent Toolkits

- **MCP toolkit** — Deriv MCP (Forex/Gold), TradingView MCP (Crypto/Stocks), Time MCP, MongoDB MCP, Redis MCP
- **Search toolkit** — Web search via Tavily for news and economic calendar events
- **Message toolkit** — Live progress notifications + user clarification

MCP servers are defined in `mcp.json`. Tool routing: Deriv for `frxXAUUSD`/`frxEURUSD`/etc., TradingView for `BINANCE:BTCUSDT`/stocks/indices.

## Core Prompt Files

Agent behavior is entirely controlled by three files in `backend/app/domain/services/prompts/`:
- `system.py` — agent identity, adaptive protocol definition, regime rules, confidence thresholds
- `planner.py` — plan structure (always: scan → configure → decide)
- `execution.py` — per-regime tool selection and decision delivery format

After editing any prompt file, restart the **Backend API** workflow.

## Running on Replit

Two workflows run in parallel:
- **Start application** — Vite dev server on port 5000, proxies `/api` → backend
- **Backend API** — FastAPI on port 8000

## Key Environment Variables

All configured in Replit env vars:
- `API_KEY` / `API_BASE` — LLM provider credentials
- `MODEL_NAME` — currently `qwen3.7-max`
- `VISION_MODEL_NAME` — `qwen2.5-vl-72b-instruct`
- `MONGODB_URI` — MongoDB Atlas connection string
- `REDIS_HOST` / `REDIS_PORT` / `REDIS_PASSWORD` — Redis Cloud
- `TAVILY_API_KEY` — web search
- `AUTH_PROVIDER` — `password` (JWT-based)
- `SEARCH_PROVIDER` — `tavily`
- `TV_PROXY_BASE` — optional proxy for TradingView scanner

## User Preferences

- API keys stay in env vars (personal project)
- No Docker — services run directly in Replit
- MongoDB Atlas + Redis Cloud for persistence (no local DB)
- Both English and Chinese documentation must be kept in sync when updating docs
