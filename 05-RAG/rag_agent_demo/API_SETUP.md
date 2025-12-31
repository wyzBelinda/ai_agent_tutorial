# RAG 生产版本 API 设置指南

## 需要的 API Key

为了运行生产版本的 RAG 系统，你需要提供以下 API Key：

### 1. OpenAI API Key

**用途：**
- 文档向量化（`text-embedding-3-large` 模型）
- 生成最终回答（`gpt-4o` 模型）

**获取方式：**
1. 访问 [OpenAI Platform](https://platform.openai.com/)
2. 注册/登录账户
3. 进入 API Keys 页面
4. 创建新的 API Key
5. 复制以 `sk-` 开头的 API Key

**设置方法：**
```bash
export OPENAI_API_KEY="sk-your-actual-api-key-here"
```

或者在 `.env` 文件中：
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

## 测试 API Key

运行测试脚本验证 API Key 是否有效：

```bash
python test_production.py
```

## 运行生产版本

设置好 API Key 后，可以运行：

```bash
# RAG Agent 版本（工具化检索）
python production_agent.py

# RAG Chain 版本（两步链路）
python production_chain.py
```

## 成本估算

**向量化成本：**
- `text-embedding-3-large`: ~$0.00013 per 1K tokens
- 博客文章约 20K tokens，成本约 $0.0026

**生成成本：**
- `gpt-4o`: ~$0.03 per 1K tokens (输入) + $0.06 per 1K tokens (输出)
- 每次问答约 2K tokens，成本约 $0.12

**总成本：** 首次构建约 $0.003，每次问答约 $0.12

## 替代方案

如果你想避免 API 成本，可以使用：

1. **本地模型**：Ollama + 本地 embeddings
2. **免费 API**：Hugging Face Inference API
3. **开源模型**：sentence-transformers + 本地 LLM

需要我帮你配置这些替代方案吗？



