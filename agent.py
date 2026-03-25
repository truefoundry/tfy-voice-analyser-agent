"""Voice Call Analyzer — DeepAgents + TFY AI Gateway + Linear MCP"""

import asyncio
import os
from pathlib import Path

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI

load_dotenv()

GATEWAY_URL = os.environ["TFY_GATEWAY_URL"]
GATEWAY_KEY = os.environ["TFY_API_KEY"]
MCP_URL = os.environ.get("TFY_MCP_GATEWAY_URL", "")
MCP_KEY = os.environ.get("TFY_MCP_GATEWAY_KEY", "")
LINEAR_PROJECT = os.environ.get("LINEAR_PROJECT", "")

TRANSCRIPT_PATH = Path(__file__).parent / "sample_transcript.txt"


def llm(name: str) -> ChatOpenAI:
    return ChatOpenAI(model=name, base_url=GATEWAY_URL, api_key=GATEWAY_KEY)


@tool
def load_transcript() -> str:
    """Load the sample call transcript."""
    return TRANSCRIPT_PATH.read_text()


# -- MCP client (shared) ---------------------------------------------------

async def get_linear_tools() -> list:
    if not MCP_URL:
        return []
    mcp = MultiServerMCPClient({
        "linear": {
            "url": MCP_URL,
            "transport": "streamable_http",
            "headers": {"Authorization": f"Bearer {MCP_KEY}"},
        },
    })
    return await mcp.get_tools()


# -- Sub-agents ------------------------------------------------------------

def build_subagents(linear_tools: list) -> list:
    return [
        {
            "name": "sentiment-analyzer",
            "description": "Analyze emotional tone and sentiment of a call transcript",
            "model": llm("flash/gemini-3-flash"),
            "system_prompt": (
                "You are a sentiment analysis expert. Given a call transcript, produce:\n"
                "1. Overall sentiment (positive/neutral/negative) with confidence score\n"
                "2. Sentiment arc — how tone shifted during the call\n"
                "3. Key emotional moments with timestamps/quotes\n"
                "4. Customer satisfaction estimate (1-10)\n"
                "Be concise. Use bullet points."
            ),
        },
        {
            "name": "action-items-creator",
            "description": "Extract action items from a call transcript and create Linear issues for each one",
            "model": llm("bedrock/global.anthropic.claude-sonnet-4-6"),
            "tools": linear_tools,
            "system_prompt": (
                "You are an expert at extracting actionable items from conversations "
                "and turning them into trackable tickets.\n\n"
                "Given a call transcript:\n"
                "1. Extract all action items — who committed to what, with deadlines if mentioned\n"
                "2. Extract open questions and decisions made\n"
                "3. For EACH action item, create a Linear issue using the save_issue tool:\n"
                "   - Title: clear, concise action item\n"
                "   - Description: full context from the call, owner, deadline\n"
                + (f"   - Project: '{LINEAR_PROJECT}'\n"
                   f"   IMPORTANT: Always create issues in the '{LINEAR_PROJECT}' project.\n"
                   if LINEAR_PROJECT else "")
                + "4. Return a summary of all action items and the Linear issues created\n\n"
                "Tag each item with the speaker. Be concise."
            ) if linear_tools else (
                "You are an expert at extracting actionable items from conversations.\n"
                "Given a call transcript, produce:\n"
                "1. Action items — who committed to what, with deadlines if mentioned\n"
                "2. Open questions — unresolved issues that need follow-up\n"
                "3. Decisions made — agreements reached during the call\n"
                "Be concise. Use bullet points. Tag each item with the speaker."
            ),
        },
        {
            "name": "call-coach",
            "description": "Provide coaching feedback on how the agent handled the call",
            "model": llm("openai-main/gpt-5-mini"),
            "system_prompt": (
                "You are a call coaching expert. Given a call transcript, produce:\n"
                "1. What went well — effective techniques used\n"
                "2. Areas for improvement — missed opportunities, awkward moments\n"
                "3. Suggested phrases — better alternatives for weak responses\n"
                "4. Overall call quality score (1-10)\n"
                "Be constructive and specific. Use examples from the transcript."
            ),
        },
    ]


SYSTEM_PROMPT = """You are a voice call analyzer. Your workflow:

1. Use load_transcript to get the call transcript
2. Delegate analysis to THREE sub-agents IN PARALLEL:
   - task(agent='sentiment-analyzer', instruction='Analyze this transcript: <full transcript>')
   - task(agent='action-items-creator', instruction='Extract action items and create Linear issues from: <full transcript>')
   - task(agent='call-coach', instruction='Coach this call: <full transcript>')
3. Combine their outputs into a single report with sections:
   **Sentiment Analysis** | **Action Items & Linear Issues** | **Coaching Feedback**
4. Return the full combined report to the user.

Always include the call title/date at the top of the report."""


# -- Graph (for langgraph dev server) --------------------------------------

async def make_graph():
    linear_tools = await get_linear_tools()
    return create_deep_agent(
        name="voice-call-analyzer",
        model=llm("bedrock/global.anthropic.claude-sonnet-4-6"),
        tools=[load_transcript],
        subagents=build_subagents(linear_tools),
        system_prompt=SYSTEM_PROMPT,
    )

# Export for langgraph.json
graph = asyncio.run(make_graph())
