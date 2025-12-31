import os
import numpy as np
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings

# 创建一个简单的本地 embeddings 类来避免 API 调用
class DummyEmbeddings(Embeddings):
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        # 为每个文档生成一个简单的随机向量
        return [np.random.rand(1536).tolist() for _ in texts]
    
    def embed_query(self, text: str) -> list[float]:
        # 为查询生成一个简单的随机向量
        return np.random.rand(1536).tolist()

# 说明：两步链路：固定一次检索 + 单次生成（此处用占位输出代替模型调用）

load_dotenv()

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
SOURCE_URL = "https://lilianweng.github.io/posts/2023-06-23-agent/"


def ensure_index():
    if os.path.exists(CHROMA_DIR) and os.listdir(CHROMA_DIR):
        return
    # 设置 USER_AGENT 避免警告
    os.environ.setdefault("USER_AGENT", "RAG-Demo/1.0")
    
    loader = WebBaseLoader(SOURCE_URL)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = splitter.split_documents(docs)
    embeddings = DummyEmbeddings()
    vector_store = Chroma(
        collection_name="lilianweng_blog",
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR,
    )
    vector_store.add_documents(splits)
    # Chroma 新版本会自动持久化到指定目录


def run_chain(query: str):
    embeddings = DummyEmbeddings()
    vector_store = Chroma(
        collection_name="lilianweng_blog",
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR,
    )
    retrieved_docs = vector_store.similarity_search(query, k=2)

    docs_content = "\n\n".join([doc.page_content for doc in retrieved_docs])

    print("[Context]\n" + docs_content[:1200] + ("..." if len(docs_content) > 1200 else ""))
    print("[Answer](基于检索上下文生成答案的占位输出)")


if __name__ == "__main__":
    print("确保索引存在...")
    ensure_index()
    print("开始运行两步链路演示...")
    run_chain("What is Task Decomposition?")



