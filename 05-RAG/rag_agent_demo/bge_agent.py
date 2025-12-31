import os
from typing import List
import numpy as np

from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_chroma import Chroma
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer

# 使用 BGE-M3 开源嵌入模型的生产版本 RAG Agent
# 无需任何 API Key，完全本地运行

load_dotenv()

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
SOURCE_URL = "https://lilianweng.github.io/posts/2023-06-23-agent/"


class BGEM3Embeddings(Embeddings):
    """BGE-M3 嵌入模型封装"""
    
    def __init__(self):
        print("🔄 正在加载 BGE-M3 模型...")
        self.model = SentenceTransformer('BAAI/bge-m3')
        print("✅ BGE-M3 模型加载完成")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """嵌入文档列表"""
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()
    
    def embed_query(self, text: str) -> List[float]:
        """嵌入查询文本"""
        embedding = self.model.encode([text], normalize_embeddings=True)
        return embedding[0].tolist()


def build_vector_store() -> Chroma:
    """构建向量库"""
    print("正在抓取网页内容...")
    loader = WebBaseLoader(SOURCE_URL)
    docs: List[Document] = loader.load()

    print("正在切分文档...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = splitter.split_documents(docs)

    print("正在生成向量嵌入（使用 BGE-M3）...")
    embeddings = BGEM3Embeddings()

    vector_store = Chroma(
        collection_name="lilianweng_blog",
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR,
    )
    vector_store.add_documents(splits)
    print(f"向量库构建完成，共 {len(splits)} 个文档片段")
    return vector_store


@tool("retrieve", return_direct=False)
def retrieve(query: str):
    """根据查询从向量库检索相关文档片段"""
    embeddings = BGEM3Embeddings()
    vector_store = Chroma(
        collection_name="lilianweng_blog",
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR,
    )
    retrieved_docs = vector_store.similarity_search(query, k=3)
    serialized = "\n\n".join(
        [
            f"来源: {doc.metadata.get('source', SOURCE_URL)}\n内容: {doc.page_content}"
            for doc in retrieved_docs
        ]
    )
    return serialized


def run_rag_agent(question: str):
    """运行完整的 RAG Agent（使用本地 LLM 或简单回答）"""
    
    # 1. 检索相关文档
    print(f"🔍 正在检索与问题相关的内容...")
    retrieved_context = retrieve.invoke({"query": question})
    
    # 2. 简单的基于规则的回答（避免需要 LLM API）
    print("🤖 正在生成回答...")
    
    # 这里可以集成你项目中的现有 LLM 封装
    # 或者使用其他开源 LLM 如 Ollama
    
    answer = f"""
基于检索到的内容，我为您整理了以下信息：

{retrieved_context[:1000]}{'...' if len(retrieved_context) > 1000 else ''}

注意：这是一个演示版本，使用了 BGE-M3 进行文档检索。
如需完整的 LLM 生成功能，可以集成你项目中的现有 LLM 封装。
"""
    
    print(f"\n📝 回答：\n{answer}")


def main():
    """主函数"""
    print("🚀 启动 BGE-M3 RAG Agent（开源版本）")
    
    # 检查并构建向量库
    if not os.path.exists(CHROMA_DIR) or not os.listdir(CHROMA_DIR):
        print("📚 首次运行，正在构建向量库...")
        build_vector_store()
    else:
        print("📚 向量库已存在，跳过构建步骤")
    
    # 交互式问答
    print("\n" + "="*50)
    print("BGE-M3 RAG Agent 已就绪！输入 'quit' 退出")
    print("="*50)
    
    while True:
        question = input("\n❓ 请输入您的问题: ").strip()
        if question.lower() in ['quit', 'exit', '退出']:
            print("👋 再见！")
            break
        
        if not question:
            continue
            
        print(f"\n处理问题: {question}")
        run_rag_agent(question)


if __name__ == "__main__":
    main()



