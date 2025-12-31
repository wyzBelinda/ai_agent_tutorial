import os
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# 说明：两步链路：固定一次检索 + 单次生成（此处用占位输出代替模型调用）

load_dotenv()

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
SOURCE_URL = "https://lilianweng.github.io/posts/2023-06-23-agent/"


def ensure_index():
    if os.path.exists(CHROMA_DIR) and os.listdir(CHROMA_DIR):
        return
    loader = WebBaseLoader(SOURCE_URL)
    docs = loader.load()
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


def run_chain(query: str):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
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
    ensure_index()
    run_chain("What is Task Decomposition?")
