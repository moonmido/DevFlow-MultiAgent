import os

from langchain.agents import create_agent
from langchain_nvidia_ai_endpoints import ChatNVIDIA

import config
from Prompts.ReviewPrompt import System_Prompt
from States.ReviewAgentOutput import ReviewState
from Tools.WebSearchTool import get_search_results

os.environ.setdefault("NVIDIA_API_KEY", config.NVIDIA_API_KEY)
os.environ.setdefault("TAVILY_API_KEY", config.TAVILY_API_KEY)

llm = ChatNVIDIA(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_completion_tokens=4096,
    timeout=600,
)

_agent = None


def create_review_agent():
    global _agent
    if _agent is None:
        _agent = create_agent(
            name="Review Agent",
            tools=[
                get_search_results,
            ],
            model=llm,
            system_prompt=System_Prompt,
            response_format=ReviewState,
        )
    return _agent
