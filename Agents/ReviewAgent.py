from langchain.agents import create_agent
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from Tools.WebSearchTool import get_search_results
from Prompts.ReviewPrompt import System_Prompt
from States.ReviewAgentOutput import ReviewState
import os 

os.environ["NVIDIA_API_KEY"] = ""

llm = ChatNVIDIA(model="openai/gpt-oss-20b")

def create_review_agent():
    agent = create_agent(
        name="Review Agent",
        tools=[
            get_search_results
        ],
        model=llm,
        system_prompt=System_Prompt,
        response_format=ReviewState
    )
    return agent





