import os

from langchain.tools import tool
from langchain_tavily import TavilySearch

import config

os.environ.setdefault("TAVILY_API_KEY", config.TAVILY_API_KEY)

_search = None


def _get_search() -> TavilySearch:
    global _search
    if _search is None:
        _search = TavilySearch(max_results=5)
    return _search


@tool(description="Retrieve web search results based on a query.")
def get_search_results(query: str):
    return _get_search().invoke({"query": query})
