import os

from langchain.agents import create_agent
from langchain_groq import ChatGroq

import config
from Prompts.DesignPrompt import Sys_Prompt
from States.DesignAgentOutput import DesignState
from Tools.KnowledgeBases.Design_Rag import get_relevant_documents

os.environ.setdefault("GROQ_API_KEY", config.GROQ_API_KEY)

llm = ChatGroq(
    model="qwen/qwen3-32b",
    temperature=0,
    max_tokens=4096,
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
