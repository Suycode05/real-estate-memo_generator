from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

def get_duckduckgo_search():
    """Initialize and return a DuckDuckGo search tool."""
    wrapper = DuckDuckGoSearchAPIWrapper(
        region="in",
        time="y",
        max_results=8,
        safesearch="moderate"
    )
    return DuckDuckGoSearchRun(api_wrapper=wrapper)

def dynamic_web_search(query: str, num_results: int = 6):
    """Perform a dynamic web search using DuckDuckGo and return results."""
    search_tool = get_duckduckgo_search()
    results = search_tool.run(query)
    return results