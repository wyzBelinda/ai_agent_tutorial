# RAG 演示（Python / LangChain 风格）

本示例在 `05-RAG/rag_agent_demo` 下包含：
- **BGE-M3 开源版本**：`bge_demo.py`（完全免费，无需 API Key）
- **OpenAI 生产版本**：`production_agent.py`、`production_chain.py`（需要 API Key）
- **测试版本**：`test_demo.py`、`test_chain.py`（使用本地 embeddings）

所有版本都会抓取网页内容或使用本地文档作为示例数据，并使用 Chroma 向量库演示。

## 准备

1) 建议使用已有虚拟环境 `.venv`：
```bash
source .venv/bin/activate
```

2) 安装依赖（与项目已用 LangChain 生态兼容）：
```bash
# BGE-M3 版本（推荐，免费）
uv add langchain langchain-community langchain-text-splitters langchain-chroma sentence-transformers torch python-dotenv chromadb

# OpenAI 版本（需要 API Key）
uv add langchain-openai
```

3) **设置环境变量（生产版本必需）**：
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

### 需要的 API Key

**生产版本需要以下 API Key：**

- **OPENAI_API_KEY**: 用于
  - `text-embedding-3-large` 模型（文档向量化）
  - `gpt-4o` 模型（生成最终回答）

> 你也可以改为其他模型与 Embeddings，或替换为本地/免费模型。

## 运行

### 🌟 BGE-M3 开源版本（推荐，完全免费）
- 运行 BGE-M3 RAG 演示（使用本地文档）：
```bash
python bge_demo.py
```

### 测试版本（无需 API Key）
- 运行 RAG Agent 测试版本（使用本地 embeddings）：
```bash
python test_demo.py
```

- 运行两步链路测试版本（使用本地 embeddings）：
```bash
python test_chain.py
```

### OpenAI 生产版本（需要 API Key）
- 运行完整的 RAG Agent（交互式问答）：
```bash
python production_agent.py
```

- 运行两步 RAG Chain（交互式问答）：
```bash
python production_chain.py
```

### 原始版本（仅演示检索，无生成）
- 运行 RAG Agent 示例（仅演示检索工具）：
```bash
python index_and_agent.py
```

- 运行两步链路示例（仅演示检索）：
```bash
python rag_chain.py
```

## 说明
- 为简化演示，默认使用 Chroma 本地向量库（`./chroma_db`）。
- 如需切换到 FAISS/Pinecone/Qdrant 等，代码注释处已留好替换入口。
- 该目录与现有 `05-RAG/agent.py` 无耦合，安全独立运行。
