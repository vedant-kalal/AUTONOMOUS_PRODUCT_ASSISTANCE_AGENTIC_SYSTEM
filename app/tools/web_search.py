from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool

@tool
def web_search_tool(query: str) -> str:
    """Search the web using DuckDuckGo."""
    search = DuckDuckGoSearchRun()
    return search.run(query)
