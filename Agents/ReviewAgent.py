import os

from Agents.structured_output import (
    GroqChatModel,
    GroqRateLimitRetry,
    GroqToolChoiceFallback,
    GroqToolStrategy,
)
from langchain.agents import create_agent

import config
from Prompts.ReviewPrompt import System_Prompt
from States.ReviewAgentOutput import ReviewState
from Tools.WebSearchTool import get_search_results

os.environ.setdefault("GROQ_API_KEY", config.GROQ_API_KEY)
os.environ.setdefault("TAVILY_API_KEY", config.TAVILY_API_KEY)

llm = GroqChatModel(
    model="openai/gpt-oss-120b",
    temperature=0,
    max_tokens=config.MODEL_MAX_TOKENS["review"],
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
            middleware=[GroqRateLimitRetry(), GroqToolChoiceFallback()],
            response_format=GroqToolStrategy(schema=ReviewState),
        )
    return _agent
