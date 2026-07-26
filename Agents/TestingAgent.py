from langchain.agents import create_agent
from langchain_nvidia_ai_endpoints import ChatNVIDIA
import os 
from Tools.FileManagementTools import create_file, read_file, overwrite_file, append_to_file, delete_file, list_files
from Prompts.TestingPrompt import System_Prompt
from States.TestingAgentOutput import TestingState

os.environ["NVIDIA_API_KEY"] = "YOUR_NVIDIA_API_KEY"

llm = ChatNVIDIA(model="openai/gpt-oss-20b",
    temperature=0,
    max_completion_tokens=4096,
    timeout=600
)


    
def create_testing_agent():
    agent = create_agent(
        name="Testing Agent",
        tools=[
            create_file,
            read_file,
            overwrite_file,
            append_to_file,
            delete_file,
            list_files
        ],
        model=llm,
        system_prompt=System_Prompt,
        response_format=TestingState
    )
    return agent

