# AI Dzeck × Claw

Autonomous AI trading analyst platform built with FastAPI + Vue 3. Users chat with an AI agent that analyzes financial markets (Forex, Crypto, Stocks) using real-time MCP-connected data sources — all streamed live.

## Architecture

| Service | Stack | Port | Entry Point |
|---|---|---|---|
| **Frontend** | Vue 3 + TypeScript + Vite + Tailwind | 5000 | `frontend/src/main.ts` |
| **Backend** | Python 3.12, FastAPI, LangChain, Beanie | 8000 | `backend/app/main.py` |

**Database:** MongoDB Atlas (cloud) + Redis Cloud (Asia Southeast)

## Agent Capabilities

The agent uses a Plan → Execute → Update loop with three active toolkits:

- **MCP toolkit** — Deriv MCP (Forex/Gold), TradingView MCP (Crypto/Stocks), Time MCP, MongoDB MCP, Redis MCP
- **Search toolkit** — Web search via Tavily for news and economic fundamentals
- **Message toolkit** — User notifications and clarification prompts

MCP servers are defined in `mcp.json`.

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

## User Preferences

- API keys stay in env vars (personal project)
- No Docker — services run directly in Replit
- MongoDB Atlas + Redis Cloud for persistence (no local DB)
- Both English and Chinese documentation must be kept in sync when updating docs
