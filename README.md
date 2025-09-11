# 「1」120分钟打造你的第一个智能体

# 先决条件
我们默认大家均：
1. 电脑上安装有Python（或者conda、miniforge等）
2. 知道如何打开命令行界面（终端）
3. 了解基本的Python语法
4. 了解某种Python开发IDE的使用（如PyCharm、Visual Studio、Cursor等）

# 环境配置（在终端中）
## 依赖包管理器安装
我们使用目前最被广泛使用现代包管理方法`uv`来进行Python环境与Python库的管理，它能够隔离各个项目之间的Python环境避免冲突，并且能够优化依赖库之间的连续多级依赖产生的冗余。首先我们需要安装uv（根据你的Python安装方式三选一）：
```
pip install uv
conda install uv
mamba install uv
```

## 初始化一个标准的 Python 项目
新建一个项目文件夹`my_agent`，并前往本文件夹目录下：
```
mkdir my_agent
cd my_agent
```
为该项目配置初始的Python环境：
```
uv init
uv venv
source .venv/bin/activate
```
## 安装必要依赖
```
uv add google-adk arxiv json os litellm
```
## 新建.env文件并写入如下信息配置API Key【在你的开发IDE中】
```
DEEPSEEK_API_KEY=【用你真实的API Key替换这里】
```
## Agent 代码实现【在你的开发IDE中】
新建`agent.py`文件并写入：
```
from google.adk.agents import Agent

import arxiv
import json
import os
from typing import List
from google.adk.models.lite_llm import LiteLlm


def search_papers(topic: str, max_results: int = 5) -> List[str]:
    """
    Search for papers on arXiv based on a topic and store their information.
    
    Args:
        topic: The topic to search for
        max_results: Maximum number of results to retrieve (default: 5)
        
    Returns:
        List of paper IDs found in the search
    """
    
    # Use arxiv to find the papers 
    client = arxiv.Client()

    # Search for the most relevant articles matching the queried topic
    search = arxiv.Search(
        query = topic,
        max_results = max_results,
        sort_by = arxiv.SortCriterion.Relevance
    )

    papers = client.results(search)
    
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
    for paper in papers:
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


root_agent = Agent(
    name="search_papers_agent",
    model=model,
    description=(
        "Agent to answer questions about the papers."
    ),
    instruction=(
        "You are a helpful agent who can answer user questions about the papers."
    ),
    tools=[search_papers, extract_info],
)
```
# 运行
在终端中（该文件夹下）运行：
```
uv run adk web
```
注：

1. Google ADK共有三种启动Agent的方式，`adk web`、`adk run`、`adk api_server`，他们分别指：
使用Google ADK封装好的Agent界面「包含了数据传输和基本的会话管理（如保证多轮对话的正常运行）的预实现」、直接以脚本的形式在终端启动Agent、将Agent作为某种公开服务开放为API，我们这里使用了最直观的`adk web`为大家演示。

2. 所有使用`uv`进行依赖管理的项目，如果想在以该`uv`环境作为编译环境运行，均需使用`uv run 【你希望运行的指令】`启动，运行的指令本身并无变化。

# 测试
当测试时可以看到类似的正确调用工具并返回，则认为你的Agent成功搭建🎉🎉🎉

![alt](https://bohrium.oss-cn-zhangjiakou.aliyuncs.com/article/24161/f4790cbbe01a4b56be0b23b047c0ef4a/5b30c5ec-740d-4170-88bb-6d78e417d4fa.png)
