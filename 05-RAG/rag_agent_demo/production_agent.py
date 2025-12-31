import os
from typing import List

from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.documents import Document

# 生产版本 RAG Agent - 完整的检索+生成流程
# 需要以下 API Key：
# - OPENAI_API_KEY: 用于 embeddings 和 chat 模型

load_dotenv()

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
SOURCE_URL = "https://lilianweng.github.io/posts/2023-06-23-agent/"


def build_vector_store() -> Chroma:
    """构建向量库"""
    print("正在抓取网页内容...")
    loader = WebBaseLoader(SOURCE_URL)
    docs: List[Document] = loader.load()

    print("正在切分文档...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = splitter.split_documents(docs)

    print("正在生成向量嵌入...")
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

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
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
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
    """运行完整的 RAG Agent"""
    # 检查 API Key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 错误：请设置 OPENAI_API_KEY 环境变量")
        return
    
    # 初始化 LLM
    llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
    
    # 1. 检索相关文档
    print(f"🔍 正在检索与问题相关的内容...")
    retrieved_context = retrieve.invoke({"query": question})
    
    # 2. 构建提示
    system_prompt = SystemMessage(content="""
你是一个智能助手，能够基于提供的上下文内容回答用户问题。

请遵循以下原则：
1. 基于提供的上下文内容回答问题
2. 如果上下文中没有相关信息，请明确说明
3. 回答要准确、简洁、有用
4. 可以引用具体的来源信息
""")
    
    user_prompt = HumanMessage(content=f"""
上下文信息：
{retrieved_context}

用户问题：{question}

请基于上述上下文信息回答用户的问题。
""")
    
    # 3. 生成回答
    print("🤖 正在生成回答...")
    response = llm.invoke([system_prompt, user_prompt])
    
    print(f"\n📝 回答：\n{response.content}")


def main():
    """主函数"""
    print("🚀 启动 RAG Agent 生产版本")
    
    # 检查并构建向量库
    if not os.path.exists(CHROMA_DIR) or not os.listdir(CHROMA_DIR):
        print("📚 首次运行，正在构建向量库...")
        build_vector_store()
    else:
        print("📚 向量库已存在，跳过构建步骤")
    
    # 交互式问答
    print("\n" + "="*50)
    print("RAG Agent 已就绪！输入 'quit' 退出")
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



