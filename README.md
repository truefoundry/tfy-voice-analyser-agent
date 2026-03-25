# Voice Call Analyzer with DeepAgents + TrueFoundry

Analyze voice call transcripts with 3 AI sub-agents running in parallel — each on a different LLM, all routed through one [TrueFoundry AI Gateway](https://www.truefoundry.com/ai-gateway). Action items are auto-created as [Linear](https://linear.app) issues via TrueFoundry MCP Gateway.

🚀 [Sign up for TrueFoundry](https://www.truefoundry.com/register) &nbsp;·&nbsp; 📖 [AI Gateway docs](https://docs.truefoundry.com/docs/ai-gateway) &nbsp;·&nbsp; 🤖 [DeepAgents](https://github.com/langchain-ai/deepagents)

---

## Architecture

```
              load_transcript()
                     │
            Planner Agent (Claude Sonnet 4.6)
                     │
        ┌────────────┼────────────┐
        │            │            │
   Sentiment    Action Items     Coach
  (Gemini 3    (Claude 4.6 +   (GPT-5
   Flash)       Linear MCP)     Mini)
        │            │            │
        └────────────┼────────────┘
                     │
              Combined Report
```

**3 LLMs, 1 API endpoint** — TFY AI Gateway handles model routing, auth, rate limiting, and observability.

---

## Quick Start

```bash
git clone <repo-url> && cd tfy-voice-analyser-agent
uv sync
cp .env.example .env
```

Fill in your credentials in `.env`:

```bash
# TFY AI Gateway (required)
TFY_GATEWAY_URL=https://gateway.truefoundry.ai
TFY_API_KEY=tfy-...

# Linear project name (optional)
LINEAR_PROJECT=

# TFY MCP Gateway for Linear (optional — skips issue creation if not set)
TFY_MCP_GATEWAY_URL=https://gateway.truefoundry.ai/your-org/mcp/linear/server
TFY_MCP_GATEWAY_KEY=tfy-...
```

Start the server:

```bash
langgraph dev --port 8888
```

This gives you:

- **API**: http://localhost:8888
- **Studio**: https://smith.langchain.com/studio/?baseUrl=http://localhost:8888
- **Docs**: http://localhost:8888/docs

---

## What It Does

1. Loads a sample support call transcript (~8 min call)
2. Spawns **3 sub-agents in parallel**, each on a different LLM via Gateway:
   - **Sentiment Analyzer** (Gemini Flash) — tone, emotional arc, CSAT score
   - **Action Items Creator** (Claude Sonnet) — extracts items + creates Linear issues via MCP
   - **Call Coach** (GPT-5 Mini) — strengths, improvements, suggested phrases
3. Combines outputs into a single report
4. Returns the report with links to created Linear issues

---

## Files

```
agent.py              — the whole thing (~130 lines)
langgraph.json        — graph config for langgraph dev
sample_transcript.txt — sample support call for demo
pyproject.toml        — dependencies
.env.example          — credential template
```

---

## What This Demonstrates

| Component | What | Why |
|-----------|------|-----|
| [DeepAgents](https://github.com/langchain-ai/deepagents) | Multi-agent orchestration with parallel sub-agents | Planning, delegation, combining results |
| [TFY AI Gateway](https://www.truefoundry.com/ai-gateway) | Single endpoint routing to 3 different LLMs | Model routing, cost control, observability |
| [TFY MCP Gateway](https://docs.truefoundry.com/docs/mcp) | Linear issue creation via MCP protocol | Secure tool access with auth + audit |
