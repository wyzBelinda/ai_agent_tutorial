# 《AI Agent 从入门到精通》课程教学代码仓库

> 本仓库包含课程配套代码与示例，支持一键使用 uv 配置环境与运行示例。

## 课程介绍
AI Agent（智能代理）作为人工智能技术的重要应用形态，正在重新定义人机交互的方式。从个人助手到企业自动化系统，从客服机器人到智能决策平台，AI Agent 的应用场景日益广泛，并正在成为连接人工智能技术与实际业务需求的重要桥梁。随着大语言模型和多模态技术的快速发展，AI Agent 已经具备了更强的理解能力、推理能力和执行能力，能够在复杂的现实场景中发挥重要作用。

本课程专为具备 Python 基础的学生设计，将全面介绍 AI Agent 的核心概念、关键技术及如何在学习和科研中的实际应用中实操构建 AI Agent，帮助学员构建对 AI Agent 技术的深入理解并跟上前沿发展。内容涵盖 Agent 基础架构、MCP 协议、提示工程、智能规划、RAG 技术、多智能体协作等核心技术，以及多模态感知、记忆系统等进阶功能，并以学习和科研场景为案例，展示 AI Agent 技术如何在日常学习和科研工作中发挥作用。

## 上课时间
- 自 9 月 17 号起每周三晚 7 点发布课程内容
- 自 9 月 24 号起每周三晚 7 点半至 8 点半进行线上答疑

## 课程目录
| 章节 | 内容 |
| --- | --- |
| 1. 120 分钟打造你的第一个智能体 | 1.1 速通理解 Agent；1.2 完成一个 Agent 的项目 |
| 2. 搭建你的 AI 工具王国：MCP 协议解密 | 2.1 如何为你的 Agent 添加工具；2.2 如何构建自己的 MCP 工具 |
| 3. 让 Agent "听懂你"：提示工程实战 | 3.1 经典 Prompt 技巧；3.2 Agent 专属 Prompt 技巧 |
| 4. 给你的 Agent 装个大脑：智能规划实战 | 4.1 经典规划器范式；4.2 给你的 Agent 装上 ReAct 武器 |
| 5. 让 Agent 读懂你的知识库：RAG 从 0 到 1 | 5.1 RAG 原理速通；5.2 上手实践 RAG 技术 |
| 6. 让 Agent 学会协作：多智能体速通 | 6.1 多智能体架构设计攻略；6.2 开发第一个多智能体 |
| 7. 打造更聪明、更稳的 Agent：进阶实战 | 7.1 增强 Agent 的感知-多模态；7.2 增强 Agent 的持久稳定-记忆系统 |
| 8. 跟上 Agent 的算法 × 工程：前沿洞察 | 8.1 前沿算法动态；8.2 前沿工程动态 |

## 仓库结构
```
/01-my_first_agent/           # 第 1 章示例：你的第一个 Agent
  ├── agent.py
  └── papers/
/02-my_mcp_agent/            # 第 2 章示例：MCP 工具与 Agent 集成
  ├── agent.py
  └── self_evolve_mcp/
pyproject.toml                # 依赖与元数据（使用 uv）
uv.lock                       # 已锁定依赖，确保可复现实验
```

## 快速开始
本仓库使用 uv 管理 Python 环境与依赖，要求 Python >= 3.12。

### 1) 安装 uv（推荐方式）
- macOS / Linux（使用 `curl`）
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
- 或使用 pipx
```bash
pipx install uv
```

验证安装：
```bash
uv --version
```

### 2) 克隆与安装依赖
```bash
git clone https://github.com/yourname/my_first_agent.git
cd my_first_agent
# 创建并使用本地虚拟环境（可选）
uv venv .venv
source .venv/bin/activate
# 安装依赖（基于 pyproject.toml / uv.lock）
uv sync
```

> 你也可以直接使用 `uv run` 在隔离环境中执行脚本，无需手动激活虚拟环境。

### 3) 配置模型密钥（以 OpenAI 为例）
项目通过 LiteLLM 统一调用多家大模型。最少需要设置一个可用的模型密钥：
```bash
# 以 OpenAI 为例
export OPENAI_API_KEY="your_openai_api_key"
```
如可用，也可配置其他厂商密钥（如 `ANTHROPIC_API_KEY`、`DEEPSEEK_API_KEY` 等）。

## 运行示例
以下命令均在仓库根目录执行。

### 示例 A：第一个 Agent（第 1 章）
```bash
uv run adk web
```
在左上角选择01-my_first_agent。

### 示例 B：MCP Agent（第 2 章）
```bash
uv run adk web
```
在左上角选择02-my_mcp_agent。

### 示例 C：自进化 MCP 工具（扩展示例）
```bash
uv run python3 02-my_mcp_agent/self_evolve_mcp/self_evolving_mcp.py
```

## 常见问题（FAQ）
- Python 版本不匹配：请确保 `python --version` ≥ 3.12。建议用 `uv venv` 创建隔离环境。
- 依赖安装缓慢：可尝试国内镜像，或多次重试 `uv sync`。
- 无法访问模型服务：确认已正确设置相应厂商 API Key，并检查网络连通性与余额配额。

## 联系方式与社群
- 课程链接：https://www.bohrium.com/courses/9912468816?tab=courses
- 课程交流群：![](wechat_qr_code.png)
  - 备注“AI Agent 课程 + 姓名/学校”，便于通过
- 小红书：11545911328

## 版权与使用
- 代码版权：MIT（详见 `LICENSE`）
- 使用说明：学习用途优先，二次分发或化用请注明来源 “WU Yuzhuo —— 《AI Agent 从入门到精通》课程”

---
如果你在安装或运行过程中遇到问题，可在 Issues 留言，或在社群中交流反馈。
