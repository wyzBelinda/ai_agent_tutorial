import os
from typing import List

from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from langchain_core.documents import Document

# 说明：
# - 该脚本实现最小可运行的 RAG Agent：
#   1) 抓取网页 -> 切分 -> 向量化 -> 写入 Chroma（本地目录 ./chroma_db）
#   2) 构建一个 "retrieve" 工具，供 Agent 在回答时检索上下文
#   3) 使用简化的调用流程演示（与文档思路一致，但在 Python 生态中落地）

load_dotenv()

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
SOURCE_URL = "https://lilianweng.github.io/posts/2023-06-23-agent/"


def build_vector_store() -> Chroma:
    loader = WebBaseLoader(SOURCE_URL)
    docs: List[Document] = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

    vector_store = Chroma(
        collection_name="lilianweng_blog",
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR,
    )
    vector_store.add_documents(splits)
    # Chroma 新版本会自动持久化到指定目录
    return vector_store


@tool("retrieve", return_direct=False)
def retrieve(query: str):
    """根据查询从向量库检索 Top-2 片段，并返回串联文本。"""
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    vector_store = Chroma(
        collection_name="lilianweng_blog",
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR,
    )
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n".join(
        [
            f"Source: {doc.metadata.get('source', SOURCE_URL)}\nContent: {doc.page_content}"
            for doc in retrieved_docs
        ]
    )
    return serialized


def run_agent_demo():
    # 简化版“Agent”调用流程：构造系统提示 + 工具调用 + 最终回答（此处仅演示检索工具产物）。
    system_prompt = SystemMessage(
        content=(
            "你可以使用一个检索工具来获取与用户问题相关的博客内容片段，"
            "并基于检索内容进行回答。"
        )
    )

    question = "What is Task Decomposition?"
    print("[System]", system_prompt.content)
    print("[User]", question)

    retrieved = retrieve.invoke({"query": question})
    print("[Tool retrieve]\n" + retrieved)

    # 这里不再发起二次 LLM 调用，仅演示检索结果；在你的项目里可用现有 LLM 封装生成最终答案。
    print("[Answer](基于检索片段生成答案的占位输出)")


if __name__ == "__main__":
    if not os.path.exists(CHROMA_DIR) or not os.listdir(CHROMA_DIR):
        build_vector_store()
    run_agent_demo()
