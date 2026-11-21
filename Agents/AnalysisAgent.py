import os

from Agents.structured_output import (
    GroqChatModel,
    GroqRateLimitRetry,
    GroqToolChoiceFallback,
    GroqToolStrategy,
)
from langchain.agents import create_agent

import config
from Prompts.AnalysisPrompt import SysPrompt
from States.AnalysisAgentOutput import AnalysisState
from Tools.KnowledgeBases.Analysis_Rag import get_relevant_documents
from Tools.WebSearchTool import get_search_results

os.environ.setdefault("GROQ_API_KEY", config.GROQ_API_KEY)
os.environ.setdefault("TAVILY_API_KEY", config.TAVILY_API_KEY)

llm = GroqChatModel(
    model="openai/gpt-oss-120b",
    temperature=0,
    max_tokens=config.MODEL_MAX_TOKENS["analysis"],
    timeout=config.MODEL_TIMEOUT_SECONDS,
)

_agent = None


def create_analysis_agent():
    global _agent
    if _agent is None:
        _agent = create_agent(
            name="AnalysisAgent",
            tools=[
                get_relevant_documents,
                get_search_results,
            ],
            model=llm,
            system_prompt=SysPrompt,
            middleware=[GroqRateLimitRetry(), GroqToolChoiceFallback()],
            response_format=GroqToolStrategy(schema=AnalysisState),
        )
    return _agent
