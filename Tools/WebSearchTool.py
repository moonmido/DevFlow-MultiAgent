import os 
from langchain_tavily import TavilySearch
from langchain.tools import tool
os.environ["TAVILY_API_KEY"] = "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" 


tavily = TavilySearch(max_results=5)

@tool(description="Retrieve web search results based on a query.")
def get_search_results(query: str):
    return tavily.invoke({"query": query})    