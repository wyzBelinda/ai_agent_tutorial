import os
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_chroma import Chroma
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer

# 使用 BGE-M3 开源嵌入模型的生产版本 RAG Chain
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
    
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """嵌入文档列表"""
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()
    
    def embed_query(self, text: str) -> list[float]:
        """嵌入查询文本"""
        embedding = self.model.encode([text], normalize_embeddings=True)
        return embedding[0].tolist()


def ensure_index():
    """确保向量库存在，如果不存在则构建"""
    if os.path.exists(CHROMA_DIR) and os.listdir(CHROMA_DIR):
        return
    
    print("📚 正在构建向量库...")
    loader = WebBaseLoader(SOURCE_URL)
    docs = loader.load()
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = splitter.split_documents(docs)
    
    embeddings = BGEM3Embeddings()
    vector_store = Chroma(
        collection_name="lilianweng_blog",
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR,
    )
    vector_store.add_documents(splits)
    print(f"✅ 向量库构建完成，共 {len(splits)} 个文档片段")


def run_rag_chain(question: str):
    """运行两步 RAG 链路"""
    
    # 1. 检索步骤
    print(f"🔍 正在检索相关内容...")
    embeddings = BGEM3Embeddings()
    vector_store = Chroma(
        collection_name="lilianweng_blog",
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR,
    )
    retrieved_docs = vector_store.similarity_search(question, k=3)
    
    # 2. 生成步骤（使用简单回答避免需要 LLM API）
    print("🤖 正在生成回答...")
    
    # 构建上下文
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])
    
    # 简单的基于规则的回答
    answer = f"""
基于检索到的内容，我为您整理了以下信息：

{context[:1000]}{'...' if len(context) > 1000 else ''}

注意：这是一个演示版本，使用了 BGE-M3 进行文档检索。
如需完整的 LLM 生成功能，可以集成你项目中的现有 LLM 封装。
"""
    
    print(f"\n📝 回答：\n{answer}")


def main():
    """主函数"""
    print("🚀 启动 BGE-M3 RAG Chain（开源版本）")
    
    # 确保向量库存在
    ensure_index()
    
    # 交互式问答
    print("\n" + "="*50)
    print("BGE-M3 RAG Chain 已就绪！输入 'quit' 退出")
    print("="*50)
    
    while True:
        question = input("\n❓ 请输入您的问题: ").strip()
        if question.lower() in ['quit', 'exit', '退出']:
            print("👋 再见！")
            break
        
        if not question:
            continue
            
        print(f"\n处理问题: {question}")
        run_rag_chain(question)


if __name__ == "__main__":
    main()



