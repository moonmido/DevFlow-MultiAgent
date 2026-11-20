import os

from langchain.agents import create_agent
from langchain_groq import ChatGroq

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

llm = ChatGroq(
    model="qwen/qwen3-32b",
    temperature=0,
    max_tokens=4096,
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
            response_format=CodingState,
        )
    return _agent
