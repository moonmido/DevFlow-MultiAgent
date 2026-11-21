import os

from Agents.structured_output import (
    GroqChatModel,
    GroqRateLimitRetry,
    GroqToolChoiceFallback,
    GroqToolStrategy,
)
from langchain.agents import create_agent

import config
from Prompts.DesignPrompt import Sys_Prompt
from States.DesignAgentOutput import DesignState
from Tools.KnowledgeBases.Design_Rag import get_relevant_documents

os.environ.setdefault("GROQ_API_KEY", config.GROQ_API_KEY)

llm = GroqChatModel(
    model="openai/gpt-oss-120b",
    temperature=0,
    max_tokens=config.MODEL_MAX_TOKENS["design"],
    timeout=config.MODEL_TIMEOUT_SECONDS,
)

_agent = None


def create_design_agent():
    global _agent
    if _agent is None:
        _agent = create_agent(
            name="DesignAgent",
            tools=[
                get_relevant_documents,
            ],
            model=llm,
            system_prompt=Sys_Prompt,
            middleware=[GroqRateLimitRetry(), GroqToolChoiceFallback()],
            response_format=GroqToolStrategy(schema=DesignState),
        )
    return _agent
