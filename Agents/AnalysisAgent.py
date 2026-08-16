import os

from langchain.agents import create_agent
from langchain_nvidia_ai_endpoints import ChatNVIDIA

import config
from Prompts.AnalysisPrompt import SysPrompt
from States.AnalysisAgentOutput import AnalysisState
from Tools.KnowledgeBases.Analysis_Rag import get_relevant_documents
from Tools.WebSearchTool import get_search_results

os.environ.setdefault("NVIDIA_API_KEY", config.NVIDIA_API_KEY)
os.environ.setdefault("TAVILY_API_KEY", config.TAVILY_API_KEY)

llm = ChatNVIDIA(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_completion_tokens=4096,
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
            response_format=AnalysisState,
        )
    return _agent
