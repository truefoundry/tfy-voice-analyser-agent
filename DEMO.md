# Demo Script

## Setup (before the demo)

1. Start the LangGraph server:
   ```bash
   cd tfy-voice-analyser-agent
   langgraph dev --port 8888
   ```

2. Start the UI:
   ```bash
   cd deep-agents-ui
   yarn dev
   ```

3. Open http://localhost:3001, click Settings, set:
   - Deployment URL: `http://localhost:8888`
   - Assistant ID: `agent`

4. Open your Linear project in another tab so you can show tickets being created live.

5. Open the TFY AI Gateway dashboard in another tab to show LLM routing.

---

## Demo Flow (~5 min)

### 1. Set the scene (30s)

> "We work with voice agents that handle customer calls. After each call, we need to analyze how it went — sentiment, action items, coaching feedback. Today I'll show you an agent that does all of this automatically using three different LLMs, routed through TrueFoundry AI Gateway, with action items pushed directly to Linear."

### 2. Show the architecture (30s)

Show the README architecture diagram or draw it:

> "One planner agent orchestrates three specialized sub-agents. Each runs on a different LLM — Gemini Flash for fast sentiment, Claude Sonnet for deep action item extraction, GPT-5 Mini for coaching. All LLM calls go through a single TFY AI Gateway endpoint. The action items sub-agent has Linear MCP tools to create real tickets."

### 3. Show the code (30s)

Open `agent.py`:

> "The entire thing is ~130 lines. DeepAgents handles the orchestration — planning, sub-agent delegation, context management. We just configure which models to use and what each sub-agent does."

Point out:
- `llm()` function — single Gateway endpoint, different model names
- 3 sub-agents with different models
- `linear_tools` passed to the action-items sub-agent
- `langgraph.json` — 5 lines to serve it

### 4. Run the demo (3 min)

In the Deep Agents UI, type:

> "Analyze the call transcript, extract action items, and create Linear issues"

While it runs, narrate:

> "The planner loads the transcript, then spawns all three sub-agents in parallel. Each is hitting a different LLM through Gateway..."

When results come back:

- **Sentiment section**: "Gemini Flash analyzed the emotional arc — you can see the tone shifted from anxious at the start to highly satisfied by the end, with a CSAT of 10/10."

- **Action Items section**: "Claude Sonnet extracted 9 action items with owners, deadlines, and priorities. And look — each one has a real Linear issue link."

- Switch to Linear tab: "Here are the actual tickets, created automatically with full context from the call."

- **Coaching section**: "GPT-5 Mini scored the agent 8/10 and gave specific improvement suggestions with example phrases."

### 5. Show the Gateway (30s)

Switch to TFY AI Gateway dashboard:

> "Every LLM call is tracked here — you can see requests fanning out to Gemini, Claude, and OpenAI. Token usage, latency, costs — all in one place. In production, you'd set rate limits and budgets per user."

### 6. Wrap up (30s)

> "So to recap: DeepAgents gives you multi-agent orchestration out of the box. TFY AI Gateway gives you one endpoint for any LLM with full observability. TFY MCP Gateway gives you secure tool access — in this case Linear, but it could be Slack, GitHub, or any MCP server. The whole thing is ~130 lines of Python."

---

## Talking Points / Q&A Prep

**Why different models for different tasks?**
> Cost optimization. Sentiment is a classification task — a fast cheap model works great. Action item extraction needs strong reasoning — Claude excels there. Coaching needs good writing — GPT-5 handles that well. Gateway makes switching models trivial.

**Why not just use one model?**
> You could! But in production, you want cost control and resilience. Gateway gives you failover — if Claude is down, route to GPT. If your budget for one provider runs out, switch to another. Same code, different config.

**Why MCP instead of direct API calls?**
> MCP gives you auth, audit logging, and tool discovery through Gateway. The agent doesn't need a Linear API key — Gateway handles that. You can revoke access, add rate limits, or swap to a different tool without changing agent code.

**How hard is it to add a new sub-agent?**
> Add a dict to the `SUBAGENTS` list. Pick a model, write a prompt. Done.

**Can this work with real-time transcripts?**
> Yes — swap `load_transcript()` for a Fireflies/Recall.ai MCP server, or just POST the transcript to the API. The analysis pipeline is the same.
