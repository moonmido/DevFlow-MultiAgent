import os

from langchain.agents import create_agent
from langchain_groq import ChatGroq

import config
from Prompts.ReviewPrompt import System_Prompt
from States.ReviewAgentOutput import ReviewState
from Tools.WebSearchTool import get_search_results

os.environ.setdefault("GROQ_API_KEY", config.GROQ_API_KEY)
os.environ.setdefault("TAVILY_API_KEY", config.TAVILY_API_KEY)

llm = ChatGroq(
    model="qwen/qwen3-32b",
    temperature=0,
    max_tokens=4096,
    timeout=config.MODEL_TIMEOUT_SECONDS,
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
