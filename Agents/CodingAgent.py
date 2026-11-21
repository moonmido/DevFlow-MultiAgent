import os

from Agents.structured_output import (
    GroqChatModel,
    GroqRateLimitRetry,
    GroqToolChoiceFallback,
    GroqToolStrategy,
)
from langchain.agents import create_agent

import config
from Prompts.CodingPrompt import System_Prompt
from States.CodingAgentOutput import CodingState
from Tools.FileManagementTools import (
    append_to_file,
    create_file,
    delete_file,
    list_files,
    overwrite_file,
    read_file,
)

os.environ.setdefault("GROQ_API_KEY", config.GROQ_API_KEY)

llm = GroqChatModel(
    model="openai/gpt-oss-120b",
    temperature=0,
    max_tokens=config.MODEL_MAX_TOKENS["coding"],
    timeout=config.MODEL_TIMEOUT_SECONDS,
)

_agent = None


def create_coding_agent():
    global _agent
    if _agent is None:
        _agent = create_agent(
            name="Coding Agent",
            tools=[
                create_file,
                read_file,
                overwrite_file,
                append_to_file,
                delete_file,
                list_files,
            ],
            model=llm,
            system_prompt=System_Prompt,
            middleware=[GroqRateLimitRetry(), GroqToolChoiceFallback()],
            response_format=GroqToolStrategy(schema=CodingState),
        )
    return _agent
