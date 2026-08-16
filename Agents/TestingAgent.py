import os

from langchain.agents import create_agent
from langchain_nvidia_ai_endpoints import ChatNVIDIA

import config
from Prompts.TestingPrompt import System_Prompt
from States.TestingAgentOutput import TestingState
from Tools.FileManagementTools import (
    append_to_file,
    create_file,
    delete_file,
    list_files,
    overwrite_file,
    read_file,
)

os.environ.setdefault("NVIDIA_API_KEY", config.NVIDIA_API_KEY)

llm = ChatNVIDIA(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_completion_tokens=4096,
    timeout=config.MODEL_TIMEOUT_SECONDS,
)

_agent = None


def create_testing_agent():
    global _agent
    if _agent is None:
        _agent = create_agent(
            name="Testing Agent",
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
            response_format=TestingState,
        )
    return _agent
