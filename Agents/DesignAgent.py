from langchain.agents import create_agent
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from Tools.KnowledgeBases.Design_Rag import get_relevant_documents
from States.DesignAgentOutput import DesignState
from Prompts.DesignPrompt import Sys_Prompt
import os 


os.environ["NVIDIA_API_KEY"] = ""

llm = ChatNVIDIA(model="openai/gpt-oss-20b")

def create_design_agent():
    agent = create_agent(
        name="DesignAgent",
        tools=[
            get_relevant_documents,
        ],
        model=llm,
        system_prompt=Sys_Prompt,
        response_format=DesignState
    )
    return agent



