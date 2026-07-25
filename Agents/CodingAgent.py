from langchain.agents import create_agent
from langchain_nvidia_ai_endpoints import ChatNVIDIA
import os 
from Tools.FileManagementTools import create_file, read_file, overwrite_file, append_to_file, delete_file, list_files
from Prompts.CodingPrompt import System_Prompt
from States.CodingAgentOutput import CodingState

os.environ["NVIDIA_API_KEY"] = "<YOUR_NVIDIA_API_KEY>"

llm = ChatNVIDIA(model="qwen/qwen3-next-80b-a3b-instruct",
    temperature=0,
    max_completion_tokens=4096,
    timeout=600
)




def create_coding_agent():
    agent = create_agent(
        name="Coding Agent",
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
        response_format=CodingState
    )
    return agent

