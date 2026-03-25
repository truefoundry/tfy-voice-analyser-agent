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
  (Gemini 3    (Claude Haiku   (GPT-5
   Flash)       4.5 + Linear    Mini)
                  MCP)
        │            │            │
        └────────────┼────────────┘
                     │
              Combined Report
```

**3 LLMs, 1 API endpoint** — TFY AI Gateway handles model routing, auth, rate limiting, and observability.

---

## Quick Start

```bash
git clone https://github.com/truefoundry/tfy-voice-analyser-agent.git && cd tfy-voice-analyser-agent
uv sync
cp .env.example .env
```

Fill in your credentials in `.env`:

```bash
# TFY AI Gateway (required)
TFY_GATEWAY_URL=https://gateway.truefoundry.ai
TFY_API_KEY=tfy-...

# Linear team name (required for issue creation)
LINEAR_TEAM=

# Linear project name (optional — if set, issues are created in this project)
LINEAR_PROJECT=

# TFY MCP Gateway for Linear (optional — skips issue creation if not set)
LINEAR_MCP_GATEWAY_URL=https://gateway.truefoundry.ai/your-org/mcp/linear/server
MCP_GATEWAY_API_KEY=tfy-...
```

### Setting up Linear via TFY MCP Gateway (optional)

To enable automatic Linear issue creation, connect the [Linear MCP server](https://linear.app) to your TrueFoundry MCP Gateway:

1. Go to your TrueFoundry dashboard and create an **MCP Gateway** endpoint
2. Connect the **Linear** MCP server to it (this requires a Linear API key with issue-creation permissions)
3. Copy the MCP Gateway URL and key into your `.env`:
   - `LINEAR_MCP_GATEWAY_URL` — the full URL to your Linear MCP endpoint (e.g. `https://gateway.truefoundry.ai/your-org/mcp/linear/server`)
   - `MCP_GATEWAY_API_KEY` - API key to access MCP gateway URL
4. Set `LINEAR_TEAM` to your Linear team name (required for issue creation)

If these are not configured, the agent will still analyze calls — it just won't create Linear tickets.

### Start the server

```bash
langgraph dev --port 8888
```

This gives you:

- **API**: http://localhost:8888
- **Studio**: https://smith.langchain.com/studio/?baseUrl=http://localhost:8888
- **Docs**: http://localhost:8888/docs

### Try it out

Open [LangGraph Studio](https://smith.langchain.com/studio/?baseUrl=http://localhost:8888) and send any message — the agent will automatically load the included `sample_transcript.txt` (a ~8 min support call) and run the full analysis pipeline.

---

## What It Does

1. Loads a sample support call transcript (~8 min call)
2. Spawns **3 sub-agents in parallel**, each on a different LLM via Gateway:
   - **Sentiment Analyzer** (Gemini Flash) — tone, emotional arc, CSAT score
   - **Action Items Creator** (Claude Haiku) — extracts items + creates Linear issues via MCP
   - **Call Coach** (GPT-5 Mini) — strengths, improvements, suggested phrases
3. Combines outputs into a single report
4. Returns the report with links to created Linear issues

---

## Customizing Models

Model names in `agent.py` must match what's registered on your TFY AI Gateway. Update these to match your setup:

```python
llm("flash/gemini-3-flash")                                   # sentiment
llm("bedrock/global.anthropic.claude-haiku-4-5-20251001-v1-0") # action items
llm("bedrock/global.anthropic.claude-sonnet-4-6")              # planner
llm("openai-main/gpt-5-mini")                                  # coaching
```

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
