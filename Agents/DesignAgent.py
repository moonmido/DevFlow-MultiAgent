import os

from langchain.agents import create_agent
from langchain_nvidia_ai_endpoints import ChatNVIDIA

import config
from Prompts.DesignPrompt import Sys_Prompt
from States.DesignAgentOutput import DesignState
from Tools.KnowledgeBases.Design_Rag import get_relevant_documents

os.environ.setdefault("NVIDIA_API_KEY", config.NVIDIA_API_KEY)

llm = ChatNVIDIA(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_completion_tokens=4096,
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
            response_format=DesignState,
        )
    return _agent
