#!/usr/bin/env python3
"""
测试 BGE-M3 开源版本 RAG 系统
无需任何 API Key，完全本地运行
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_imports():
    """测试所有必要的导入"""
    try:
        from sentence_transformers import SentenceTransformer
        from langchain_chroma import Chroma
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_community.document_loaders import WebBaseLoader
        print("✅ 所有依赖导入成功")
        return True
    except ImportError as e:
        print(f"❌ 导入错误：{e}")
        print("请运行：uv add sentence-transformers torch langchain-chroma langchain-community langchain-text-splitters")
        return False

def test_bge_model():
    """测试 BGE-M3 模型加载"""
    try:
        print("🔄 正在下载/加载 BGE-M3 模型...")
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('BAAI/bge-m3')
        print("✅ BGE-M3 模型加载成功")
        return True
    except Exception as e:
        print(f"❌ BGE-M3 模型加载失败：{e}")
        return False

def test_embeddings():
    """测试 embeddings 功能"""
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('BAAI/bge-m3')
        
        # 测试中文
        chinese_text = "这是一个中文测试文档"
        chinese_embedding = model.encode([chinese_text], normalize_embeddings=True)
        
        # 测试英文
        english_text = "This is an English test document"
        english_embedding = model.encode([english_text], normalize_embeddings=True)
        
        print(f"✅ Embeddings 测试成功")
        print(f"   中文向量维度：{len(chinese_embedding[0])}")
        print(f"   英文向量维度：{len(english_embedding[0])}")
        return True
    except Exception as e:
        print(f"❌ Embeddings 测试失败：{e}")
        return False

def test_similarity():
    """测试相似度计算"""
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('BAAI/bge-m3')
        
        texts = [
            "人工智能和机器学习",
            "AI and machine learning", 
            "今天天气很好"
        ]
        
        embeddings = model.encode(texts, normalize_embeddings=True)
        
        # 计算相似度
        import numpy as np
        similarity_01 = np.dot(embeddings[0], embeddings[1])
        similarity_02 = np.dot(embeddings[0], embeddings[2])
        
        print(f"✅ 相似度测试成功")
        print(f"   '人工智能' vs 'AI': {similarity_01:.3f}")
        print(f"   '人工智能' vs '天气': {similarity_02:.3f}")
        return True
    except Exception as e:
        print(f"❌ 相似度测试失败：{e}")
        return False

def main():
    """运行所有测试"""
    print("🧪 开始测试 BGE-M3 开源版本 RAG 系统...")
    print("="*50)
    
    tests = [
        ("依赖导入检查", test_imports),
        ("BGE-M3 模型加载", test_bge_model),
        ("Embeddings 功能", test_embeddings),
        ("相似度计算", test_similarity),
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
        print("🎉 所有测试通过！可以运行 BGE-M3 版本")
        print("\n运行命令：")
        print("  python bge_agent.py")
        print("  python bge_chain.py")
    else:
        print("❌ 部分测试失败，请检查上述错误信息")
        sys.exit(1)

if __name__ == "__main__":
    main()



