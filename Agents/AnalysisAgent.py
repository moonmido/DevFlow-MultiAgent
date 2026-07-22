from langchain.agents import create_agent
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from Tools.KnowledgeBases.Analysis_Rag import get_relevant_documents
from Tools.WebSearchTool import get_search_results
from Prompts.AnalysisPrompt import SysPrompt
from States.AnalysisAgentOutput import AnalysisState
import os 

os.environ["NVIDIA_API_KEY"] = ""

llm = ChatNVIDIA(model="openai/gpt-oss-20b")

def create_analysis_agent():
    agent = create_agent(
        name="AnalysisAgent",
        tools=[
            get_relevant_documents,
            get_search_results
        ],
        model=llm,
        system_prompt=SysPrompt,
        response_format=AnalysisState
    )
    return agent

