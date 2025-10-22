#!/usr/bin/env python
"""多数据源知识库使用示例"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.datasource_config import get_datasource_manager
from src.vectorstore.knowledge_base_manager import get_knowledge_base_manager
from langchain.embeddings import OpenAIEmbeddings
from src.utils.config import settings


def example_1_list_datasources():
    """示例 1: 列出所有数据源配置"""
    print("\n" + "=" * 80)
    print("示例 1: 列出所有数据源配置")
    print("=" * 80)

    # 获取数据源管理器
    datasource_manager = get_datasource_manager()

    # 列出所有数据源
    datasource_manager.list_datasources()

    # 获取启用的数据源
    enabled_datasources = datasource_manager.get_enabled_datasources()
    print(f"\n启用的数据源数量: {len(enabled_datasources)}")


def example_2_load_knowledge_bases():
    """示例 2: 加载已有的知识库"""
    print("\n" + "=" * 80)
    print("示例 2: 加载已有的知识库")
    print("=" * 80)

    # 创建嵌入模型
    embeddings = OpenAIEmbeddings(
        model=settings.embedding_model,
        openai_api_key=settings.openai_api_key
    )

    # 获取知识库管理器
    kb_manager = get_knowledge_base_manager(embedding_model=embeddings)

    # 加载所有知识库
    kb_manager.load_all()

    # 列出知识库
    kb_manager.list_knowledge_bases()


def example_3_search_single_kb():
    """示例 3: 搜索单个知识库"""
    print("\n" + "=" * 80)
    print("示例 3: 搜索单个知识库")
    print("=" * 80)

    # 创建嵌入模型
    embeddings = OpenAIEmbeddings(
        model=settings.embedding_model,
        openai_api_key=settings.openai_api_key
    )

    # 获取知识库管理器
    kb_manager = get_knowledge_base_manager(embedding_model=embeddings)

    # 加载知识库
    kb_manager.load_all()

    # 搜索查询
    query = "用户表有哪些字段？"
    print(f"\n查询: {query}\n")

    # 搜索第一个知识库
    if kb_manager.knowledge_bases:
        kb_name = list(kb_manager.knowledge_bases.keys())[0]
        print(f"搜索知识库: {kb_name}\n")

        results = kb_manager.search(query, datasource_name=kb_name, k=3)

        for kb, docs in results.items():
            print(f"\n知识库: {kb}")
            print("-" * 60)
            for i, doc in enumerate(docs, 1):
                print(f"\n结果 {i}:")
                print(f"内容: {doc.page_content[:200]}...")
                print(f"元数据: {doc.metadata}")
    else:
        print("⚠️  没有可用的知识库")


def example_4_search_all_kbs():
    """示例 4: 搜索所有知识库"""
    print("\n" + "=" * 80)
    print("示例 4: 搜索所有知识库")
    print("=" * 80)

    # 创建嵌入模型
    embeddings = OpenAIEmbeddings(
        model=settings.embedding_model,
        openai_api_key=settings.openai_api_key
    )

    # 获取知识库管理器
    kb_manager = get_knowledge_base_manager(embedding_model=embeddings)

    # 加载知识库
    kb_manager.load_all()

    # 搜索查询
    query = "订单相关的表"
    print(f"\n查询: {query}\n")

    # 搜索所有知识库
    results = kb_manager.search(query, k=2)

    print(f"\n找到 {len(results)} 个知识库的结果:\n")

    for kb_name, docs in results.items():
        print(f"\n知识库: {kb_name}")
        print("-" * 60)
        print(f"找到 {len(docs)} 个相关文档")

        for i, doc in enumerate(docs, 1):
            print(f"\n  结果 {i}:")
            print(f"  内容: {doc.page_content[:150]}...")


def example_5_qa_with_kb():
    """示例 5: 基于知识库的问答"""
    print("\n" + "=" * 80)
    print("示例 5: 基于知识库的问答")
    print("=" * 80)

    from src.rag.rag_retriever import RAGRetriever
    from src.llm.llm_factory import LLMFactory

    # 创建嵌入模型
    embeddings = OpenAIEmbeddings(
        model=settings.embedding_model,
        openai_api_key=settings.openai_api_key
    )

    # 获取知识库管理器
    kb_manager = get_knowledge_base_manager(embedding_model=embeddings)

    # 加载知识库
    kb_manager.load_all()

    if not kb_manager.knowledge_bases:
        print("⚠️  没有可用的知识库")
        return

    # 获取第一个知识库
    kb_name = list(kb_manager.knowledge_bases.keys())[0]
    kb = kb_manager.knowledge_bases[kb_name]

    print(f"\n使用知识库: {kb_name}\n")

    # 创建 LLM
    llm = LLMFactory.create_llm(
        provider=settings.default_llm_provider,
        model_name=settings.default_model_name,
        temperature=0.7
    )

    # 创建 RAG 检索器
    rag_retriever = RAGRetriever(
        vectorstore_manager=kb.vectorstore_manager,
        llm=llm,
        top_k=3
    )

    # 提问
    questions = [
        "数据库中有哪些表？",
        "用户表的结构是什么？",
        "订单表包含哪些字段？"
    ]

    for question in questions:
        print(f"\n问题: {question}")
        print("-" * 60)

        result = rag_retriever.query(question, return_sources=True)

        print(f"回答: {result['answer']}\n")

        if result.get('sources'):
            print("参考来源:")
            for i, source in enumerate(result['sources'][:2], 1):
                print(f"  {i}. {source['metadata'].get('table_name', 'N/A')}")


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("🚀 多数据源知识库使用示例")
    print("=" * 80)

    try:
        # 运行示例
        example_1_list_datasources()

        # 注意：以下示例需要先运行导入脚本创建知识库
        # python scripts/import_datasources.py --all

        # example_2_load_knowledge_bases()
        # example_3_search_single_kb()
        # example_4_search_all_kbs()
        # example_5_qa_with_kb()

        print("\n" + "=" * 80)
        print("✅ 示例运行完成！")
        print("=" * 80)
        print("\n提示:")
        print("1. 如需运行其他示例，请先运行导入脚本:")
        print("   python scripts/import_datasources.py --all")
        print("2. 取消注释 main() 函数中的其他示例代码")
        print("=" * 80 + "\n")

    except Exception as e:
        print(f"\n❌ 错误: {str(e)}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

