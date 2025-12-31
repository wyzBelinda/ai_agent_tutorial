import os
from typing import List

from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer

# 使用 BGE-M3 开源嵌入模型 + 本地文档的 RAG Agent
# 无需任何 API Key，完全本地运行

load_dotenv()

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")

# 使用本地文档内容
LOCAL_DOCS = [
    {
        "content": """
人工智能（AI）是计算机科学的一个分支，旨在创建能够执行通常需要人类智能的任务的系统。
机器学习是人工智能的一个子领域，专注于开发能够从数据中学习的算法。

深度学习是机器学习的一个分支，使用多层神经网络来模拟人脑的工作方式。
这些网络可以自动学习数据的复杂模式和特征，无需人工干预。

自然语言处理（NLP）是人工智能的另一个重要分支，专注于让计算机理解、解释和生成人类语言。
现代NLP系统使用深度学习技术，如Transformer架构，来理解语言的上下文和语义。
""",
        "source": "AI基础知识"
    },
    {
        "content": """
RAG（Retrieval-Augmented Generation）是一种结合检索和生成的技术。
它首先从知识库中检索相关信息，然后使用这些信息来生成更准确的回答。

RAG系统通常包含以下组件：
1. 文档索引：将文档切分并转换为向量嵌入
2. 检索器：根据查询找到最相关的文档片段
3. 生成器：基于检索到的内容生成最终回答

这种方法的优势在于能够提供基于事实的回答，减少幻觉问题。
""",
        "source": "RAG技术介绍"
    },
    {
        "content": """
BGE-M3是北京智源人工智能研究院开发的多语言嵌入模型。
它支持100多种语言，在多个基准测试中表现优异。

BGE-M3的特点：
- 多语言支持：支持中文、英文等多种语言
- 高质量嵌入：在多个任务上达到SOTA性能
- 开源免费：可以免费使用和部署
- 向量维度：1024维

该模型特别适合构建多语言RAG系统。
""",
        "source": "BGE-M3模型介绍"
    }
]


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
    print("正在处理本地文档...")
    
    # 创建文档对象
    docs = []
    for doc_data in LOCAL_DOCS:
        doc = Document(
            page_content=doc_data["content"],
            metadata={"source": doc_data["source"]}
        )
        docs.append(doc)

    print("正在切分文档...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    splits = splitter.split_documents(docs)

    print("正在生成向量嵌入（使用 BGE-M3）...")
    embeddings = BGEM3Embeddings()

    vector_store = Chroma(
        collection_name="local_docs",
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
        collection_name="local_docs",
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR,
    )
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        [
            f"来源: {doc.metadata.get('source', '未知')}\n内容: {doc.page_content}"
            for doc in retrieved_docs
        ]
    )
    return serialized


def run_rag_agent(question: str):
    """运行完整的 RAG Agent"""
    
    # 1. 检索相关文档
    print(f"🔍 正在检索与问题相关的内容...")
    retrieved_context = retrieve.invoke({"query": question})
    
    # 2. 简单的基于规则的回答
    print("🤖 正在生成回答...")
    
    answer = f"""
基于检索到的内容，我为您整理了以下信息：

{retrieved_context}

注意：这是一个演示版本，使用了 BGE-M3 进行文档检索。
检索到的内容已经按照相关性排序，最相关的内容在前面。
"""
    
    print(f"\n📝 回答：\n{answer}")


def main():
    """主函数"""
    print("🚀 启动 BGE-M3 RAG Agent（本地文档版本）")
    
    # 检查并构建向量库
    if not os.path.exists(CHROMA_DIR) or not os.listdir(CHROMA_DIR):
        print("📚 首次运行，正在构建向量库...")
        build_vector_store()
    else:
        print("📚 向量库已存在，跳过构建步骤")
    
    # 交互式问答
    print("\n" + "="*50)
    print("BGE-M3 RAG Agent 已就绪！输入 'quit' 退出")
    print("可尝试的问题：")
    print("- 什么是人工智能？")
    print("- RAG技术是什么？")
    print("- BGE-M3模型有什么特点？")
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



