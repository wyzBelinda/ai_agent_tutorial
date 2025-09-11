# my-agent

一个基于 LiteLLM 与 `google-adk` 构建的小型论文检索与信息提取 Agent。它使用 `arxiv` 库从 arXiv 搜索论文，将检索结果保存为本地 JSON，支持根据论文 ID 快速查看已保存的信息。

## 功能特性
- **搜索论文**：根据主题关键词检索 arXiv 上的论文，并将结果保存到本地 `papers_info.json`。
- **提取信息**：通过论文短 ID（如 `2401.01234`）在本地检索并返回该论文的标题、作者、摘要、PDF 链接与发布日期。
- **Agent 集成**：提供了一个 `google.adk.agents.Agent`（见 `my_first_agent/agent.py` 中的 `root_agent`），可将上述函数以工具的形式暴露给 LLM。

## 目录结构
```
my_agent/
├─ main.py                         # 入口示例（当前仅打印问候语）
├─ my_first_agent/
│  ├─ __init__.py
│  └─ agent.py                     # 搜索与信息提取工具 + root_agent 定义
├─ pyproject.toml                  # 项目配置（依赖、Python 版本等）
├─ uv.lock                         # uv 锁文件（若使用 uv 管理依赖）
└─ README.md
```

## 环境要求
- Python >= 3.12

## 安装
你可以使用 `uv` 或 `pip` 安装依赖。

- 使用 uv（推荐）：
```bash
# 确保已安装 uv： https://docs.astral.sh/uv/
uv sync
```

- 使用 pip：
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -U pip
pip install -e .
```

## 依赖
`pyproject.toml` 中声明了以下主要依赖：
- `arxiv`：访问 arXiv API
- `google-adk`：Agent 框架
- `litellm`：模型调用统一接口

## 模型与密钥配置
本项目通过 `litellm.LiteLlm` 指定模型，示例位于 `my_first_agent/agent.py`：
```python
from google.adk.models.lite_llm import LiteLlm

use_model = "deepseek"
if use_model == "deepseek":
    model = LiteLlm(model="deepseek/deepseek-chat")
if use_model == "gpt-4o":
    model = LiteLlm(model="azure/gpt-4o")
```
请根据所选厂商配置相应的环境变量（示例）：
- DeepSeek: 设置 `DEEPSEEK_API_KEY`
- Azure OpenAI gpt-4o: 设置 `AZURE_OPENAI_API_KEY` 以及必要的 `AZURE_OPENAI_ENDPOINT`、`AZURE_OPENAI_API_VERSION`

具体变量名可能因 `litellm` 版本与提供商不同而异，请参考 `litellm` 文档及对应大模型提供商的说明。设置环境变量示例：
```bash
export DEEPSEEK_API_KEY="<your_key>"
# 或者（Azure OpenAI）
export AZURE_OPENAI_API_KEY="<your_key>"
export AZURE_OPENAI_ENDPOINT="<your_endpoint>"
export AZURE_OPENAI_API_VERSION="2024-02-15-preview"
```

> 注：`arxiv` 检索无需 API Key。

## 快速开始
### 方式一：直接运行示例入口
```bash
python main.py
```
当前 `main.py` 仅用于演示入口结构，会输出：
```
Hello from my-agent!
```

### 方式二：以函数形式使用工具
你可以直接调用 `my_first_agent/agent.py` 中的两个工具函数：

```python
from my_first_agent.agent import search_papers, extract_info

# 1) 按主题检索论文并保存信息
topic = "large language model alignment"
paper_ids = search_papers(topic, max_results=5)
print("检索到的论文短 ID:", paper_ids)

# 2) 根据短 ID 提取已保存的信息（示例：取第一篇）
if paper_ids:
    info = extract_info(paper_ids[0])
    print("论文信息:\n", info)
```

### 方式三：通过 Agent 使用工具
`root_agent` 已将上述函数注册为工具，你可以将自然语言问题交给 Agent 处理：

```python
from my_first_agent.agent import root_agent

# 示例：让 Agent 去检索某一主题的论文
user_query = "帮我找 3 篇关于 RAG 的综述论文，并保存"
response = root_agent.run(user_query)
print(response)
```

> 提示：`google-adk` 的 Agent 行为依赖所选模型及工具注册方式，`run` 的具体用法请根据你所用的 `google-adk` 版本查看文档；如果你更倾向显式调用，可直接使用上面的函数式用法。

## 数据保存位置
当你调用 `search_papers(topic, ...)` 后，程序会在当前工作目录下创建：
```
./papers/<topic_下划线格式>/papers_info.json
```
其中会保存检索到论文的元信息；随后可用 `extract_info(<paper_id>)` 读取其中的内容。

## 常见问题
- **检索为空或较少？** 尝试更换或精炼关键词，或增大 `max_results`。
- **无法调用模型/报鉴权错误？** 请确认已正确设置对应厂商的 API Key 与必需的环境变量。
- **编码或字符显示问题？** 建议终端与编辑器统一为 UTF-8 编码。

## 许可证
当前未指定许可证。如需开源发布，请补充相应 LICENSE 文件。
