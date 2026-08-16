import concurrent.futures
import os

from langchain.tools import tool
from langchain_tavily import TavilySearch

import config

os.environ.setdefault("TAVILY_API_KEY", config.TAVILY_API_KEY)

SEARCH_TIMEOUT = int(os.getenv("DEVFLOW_SEARCH_TIMEOUT", "20"))

_search = None


def _get_search() -> TavilySearch:
    global _search
    if _search is None:
        _search = TavilySearch(max_results=5)
    return _search


@tool(description="Retrieve web search results based on a query.")
def get_search_results(query: str):
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(_get_search().invoke, {"query": query})
            try:
                results = future.result(timeout=SEARCH_TIMEOUT)
            except concurrent.futures.TimeoutError:
                return (
                    "[web search timed out and returned no results. "
                    "Proceed without web references.]"
                )
        if results and results.get("results"):
            return results
        return (
            "[web search returned no results. "
            "Proceed without web references.]"
        )
    except Exception as exc:  # noqa: BLE001
        return f"[web search failed ({type(exc).__name__}). Proceed without web references.]"
