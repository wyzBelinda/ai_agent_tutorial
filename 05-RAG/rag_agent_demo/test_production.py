#!/usr/bin/env python3
"""
测试生产版本 RAG 系统
需要真实的 OPENAI_API_KEY 环境变量
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_api_key():
    """测试 API Key 是否设置"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 错误：未设置 OPENAI_API_KEY 环境变量")
        print("请设置：export OPENAI_API_KEY='your-api-key'")
        return False
    
    if api_key.startswith("sk-"):
        print("✅ API Key 格式正确")
        return True
    else:
        print("⚠️  API Key 格式可能不正确（应该以 'sk-' 开头）")
        return False

def test_imports():
    """测试所有必要的导入"""
    try:
        from langchain_openai import OpenAIEmbeddings, ChatOpenAI
        from langchain_chroma import Chroma
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_community.document_loaders import WebBaseLoader
        print("✅ 所有依赖导入成功")
        return True
    except ImportError as e:
        print(f"❌ 导入错误：{e}")
        print("请运行：uv add langchain langchain-openai langchain-chroma langchain-community langchain-text-splitters")
        return False

def test_embeddings():
    """测试 embeddings 功能"""
    try:
        from langchain_openai import OpenAIEmbeddings
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")  # 使用更便宜的模型测试
        test_text = "这是一个测试文档"
        result = embeddings.embed_query(test_text)
        print(f"✅ Embeddings 测试成功，向量维度：{len(result)}")
        return True
    except Exception as e:
        print(f"❌ Embeddings 测试失败：{e}")
        return False

def test_chat():
    """测试聊天模型功能"""
    try:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        response = llm.invoke("Hello, this is a test. Please respond with 'Test successful'.")
        print(f"✅ Chat 模型测试成功：{response.content}")
        return True
    except Exception as e:
        print(f"❌ Chat 模型测试失败：{e}")
        return False

def main():
    """运行所有测试"""
    print("🧪 开始测试生产版本 RAG 系统...")
    print("="*50)
    
    tests = [
        ("API Key 检查", test_api_key),
        ("依赖导入检查", test_imports),
        ("Embeddings 功能", test_embeddings),
        ("Chat 模型功能", test_chat),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} 失败")
    
    print("\n" + "="*50)
    print(f"📊 测试结果：{passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！可以运行生产版本")
        print("\n运行命令：")
        print("  python production_agent.py")
        print("  python production_chain.py")
    else:
        print("❌ 部分测试失败，请检查上述错误信息")
        sys.exit(1)

if __name__ == "__main__":
    main()



