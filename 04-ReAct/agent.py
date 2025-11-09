from google.adk.agents import Agent

import arxiv
import json
import os
from typing import List
import time
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams, StreamableHTTPConnectionParams
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams
from mcp import StdioServerParameters
from dotenv import load_dotenv
from . import prompt
from google.adk.planners import PlanReActPlanner


load_dotenv()

PAPER_DIR='my_mcp_agent/papers'

def search_papers(topic: str, max_results: int = 5) -> List[str]:
    """
    Search for papers on arXiv based on a topic and store their information.
    
    Args:
        topic: The topic to search for
        max_results: Maximum number of results to retrieve (default: 5)
        
    Returns:
        List of paper IDs found in the search
    """
    
    # Use arxiv with chunked paging and retries to avoid empty-page exceptions
    # add internal retry + polite delay to reduce server-side glitches
    client = arxiv.Client(num_retries=3, delay_seconds=2)
    collected: List[arxiv.Result] = []

    # 当前 arxiv 库版本不支持 Search 的 start 参数，故不做分页偏移
    search = arxiv.Search(
        query=topic,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
    )

    # simple retry with exponential backoff
    attempt = 0
    max_attempts = 3
    backoff_seconds = 1.0
    page_results: List[arxiv.Result] = []
    while attempt < max_attempts:
        try:
            page_results = list(client.results(search))
            break
        except arxiv.UnexpectedEmptyPageError:
            # 显式处理：将其视为无结果
            page_results = []
            break
        except Exception:
            attempt += 1
            if attempt >= max_attempts:
                page_results = []
                break
            time.sleep(backoff_seconds)
            backoff_seconds *= 2

    collected.extend(page_results)
    
    # Create directory for this topic
    path = os.path.join(PAPER_DIR, topic.lower().replace(" ", "_"))
    os.makedirs(path, exist_ok=True)
    
    file_path = os.path.join(path, "papers_info.json")

    # Try to load existing papers info
    try:
        with open(file_path, "r") as json_file:
            papers_info = json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError):
        papers_info = {}

    # Process each paper and add to papers_info  
    paper_ids = []
    for paper in collected:
        paper_ids.append(paper.get_short_id())
        paper_info = {
            'title': paper.title,
            'authors': [author.name for author in paper.authors],
            'summary': paper.summary,
            'pdf_url': paper.pdf_url,
            'published': str(paper.published.date())
        }
        papers_info[paper.get_short_id()] = paper_info
    
    # Save updated papers_info to json file
    with open(file_path, "w") as json_file:
        json.dump(papers_info, json_file, indent=2)
    
    print(f"Results are saved in: {file_path}")
    
    return paper_ids

def extract_info(paper_id: str) -> str:
    """
    Search for information about a specific paper across all topic directories.
    
    Args:
        paper_id: The ID of the paper to look for
        
    Returns:
        JSON string with paper information if found, error message if not found
    """
 
    for item in os.listdir(PAPER_DIR):
        item_path = os.path.join(PAPER_DIR, item)
        if os.path.isdir(item_path):
            file_path = os.path.join(item_path, "papers_info.json")
            if os.path.isfile(file_path):
                try:
                    with open(file_path, "r") as json_file:
                        papers_info = json.load(json_file)
                        if paper_id in papers_info:
                            return json.dumps(papers_info[paper_id], indent=2)
                except (FileNotFoundError, json.JSONDecodeError) as e:
                    print(f"Error reading {file_path}: {str(e)}")
                    continue
    
    return f"There's no saved information related to paper {paper_id}."

use_model = "deepseek"

if use_model == "deepseek":
    model = LiteLlm(model="deepseek/deepseek-chat")
if use_model == "gpt-4o":
    model = LiteLlm(model="azure/gpt-4o")


# https://github.com/34892002/bilibili-mcp-js
bilibili_mcp = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command='npx',
            args=['bilibili-mcp'],
        ),
        timeout=50,
    ),
)


load_dotenv()
tavily_api_key = os.getenv("TAVILY_API_KEY")
tavily_api_url = f"https://mcp.tavily.com/mcp/?tavilyApiKey={tavily_api_key}"
tavily_mcp = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=tavily_api_url,
        timeout=30,  # 增加超时时间到30秒
    ),
)

self_evolving_mcp = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command='python3',
            args=['self_evolve_mcp/self_evolving_mcp.py'],
        ),
        timeout=5,
    ),
)



root_agent = Agent(
    name="search_papers_agent",
    model=model,
    planner=PlanReActPlanner(), 
    description=(
        "Agent to answer questions about the papers."
    ),
    instruction=prompt.ACADEMIC_COORDINATOR_PROMPT,
    tools=[search_papers, extract_info, bilibili_mcp, tavily_mcp],
)

# source .venv/bin/activate
# uv run adk web
