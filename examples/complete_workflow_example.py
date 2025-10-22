#!/usr/bin/env python
"""完整工作流示例 - 从配置到查询的完整流程"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def example_complete_workflow():
    """完整工作流示例"""
    print("\n" + "=" * 80)
    print("🚀 完整工作流示例")
    print("=" * 80)

    # ========== 步骤 1: 加载配置 ==========
    print("\n" + "=" * 80)
    print("步骤 1: 加载配置")
    print("=" * 80)

    from src.utils.config import settings
    from src.utils.datasource_config import get_datasource_manager

    print(f"✓ LLM 提供商: {settings.default_llm_provider}")
    print(f"✓ 模型名称: {settings.default_model_name}")
    print(f"✓ 向量数据库类型: {settings.vector_db_type}")

    # 加载数据源配置
    datasource_manager = get_datasource_manager()
    print(f"✓ 数据源数量: {len(datasource_manager.get_all_datasources())}")
    print(f"✓ 启用的数据源: {len(datasource_manager.get_enabled_datasources())}")

    # ========== 步骤 2: 初始化嵌入模型 ==========
    print("\n" + "=" * 80)
    print("步骤 2: 初始化嵌入模型")
    print("=" * 80)

    from langchain.embeddings import OpenAIEmbeddings

    embeddings = OpenAIEmbeddings(
        model=settings.embedding_model,
        openai_api_key=settings.openai_api_key
    )
    print(f"✓ 嵌入模型: {settings.embedding_model}")

    # ========== 步骤 3: 创建知识库管理器 ==========
    print("\n" + "=" * 80)
    print("步骤 3: 创建知识库管理器")
    print("=" * 80)

    from src.vectorstore.knowledge_base_manager import get_knowledge_base_manager

    kb_manager = get_knowledge_base_manager(
        datasource_manager=datasource_manager,
        embedding_model=embeddings
    )
    print("✓ 知识库管理器已创建")

    # ========== 步骤 4: 加载知识库 ==========
    print("\n" + "=" * 80)
    print("步骤 4: 加载知识库")
    print("=" * 80)

    try:
        kb_manager.load_all()
        kb_manager.list_knowledge_bases()
    except Exception as e:
        print(f"⚠️  加载知识库失败: {str(e)}")
        print("💡 提示: 请先运行导入脚本")
        print("   python scripts/import_datasources.py --all")
        return

    if not kb_manager.knowledge_bases:
        print("⚠️  没有可用的知识库")
        return

    # ========== 步骤 5: 搜索知识库 ==========
    print("\n" + "=" * 80)
    print("步骤 5: 搜索知识库")
    print("=" * 80)

    queries = [
        "用户表有哪些字段？",
        "订单相关的表",
        "数据库中有哪些主键？"
    ]

    for query in queries:
        print(f"\n查询: {query}")
        print("-" * 60)

        try:
            results = kb_manager.search(query, k=2)

            for kb_name, docs in results.items():
                if docs:
                    print(f"\n知识库: {kb_name}")
                    for i, doc in enumerate(docs, 1):
                        print(f"  结果 {i}:")
                        print(f"    内容: {doc.page_content[:100]}...")
                        print(f"    表名: {doc.metadata.get('table_name', 'N/A')}")
        except Exception as e:
            print(f"  ❌ 搜索失败: {str(e)}")

    # ========== 步骤 6: 创建 LLM ==========
    print("\n" + "=" * 80)
    print("步骤 6: 创建 LLM")
    print("=" * 80)

    from src.llm.llm_factory import LLMFactory

    llm = LLMFactory.create_llm(
        provider=settings.default_llm_provider,
        model_name=settings.default_model_name,
        temperature=0.7,
        api_key=settings.openai_api_key
    )
    print(f"✓ LLM 已创建: {settings.default_model_name}")

    # ========== 步骤 7: 创建 RAG 检索器并问答 ==========
    print("\n" + "=" * 80)
    print("步骤 7: 基于知识库的智能问答")
    print("=" * 80)

    from src.rag.rag_retriever import RAGRetriever

    # 获取第一个知识库
    kb_name = list(kb_manager.knowledge_bases.keys())[0]
    kb = kb_manager.knowledge_bases[kb_name]

    print(f"\n使用知识库: {kb_name}")

    # 创建 RAG 检索器
    rag_retriever = RAGRetriever(
        vectorstore_manager=kb.vectorstore_manager,
        llm=llm,
        top_k=3
    )

    questions = [
        "数据库中有哪些表？请列出主要的表名。",
        "用户表的结构是什么？包含哪些字段？",
    ]

    for question in questions:
        print(f"\n问题: {question}")
        print("-" * 60)

        try:
            result = rag_retriever.query(question, return_sources=True)

            print(f"回答: {result['answer']}\n")

            if result.get('sources'):
                print("参考来源:")
                for i, source in enumerate(result['sources'][:2], 1):
                    table_name = source['metadata'].get('table_name', 'N/A')
                    print(f"  {i}. 表: {table_name}")
        except Exception as e:
            print(f"  ❌ 查询失败: {str(e)}")

    # ========== 步骤 8: 使用 Agent 进行对话 ==========
    print("\n" + "=" * 80)
    print("步骤 8: 使用 Agent 进行对话")
    print("=" * 80)

    from src.agent.data_assistant import DataAssistantAgent

    agent = DataAssistantAgent(
        llm=llm,
        vectorstore_manager=kb.vectorstore_manager,
        rag_retriever=rag_retriever,
        agent_name="数据小助手",
        agent_description="我是你的数据库助手，可以帮你查询和分析数据"
    )

    print("✓ Agent 已创建")

    conversations = [
        "你好，请介绍一下你自己",
        "数据库中有哪些表？",
        "用户表的主要字段有哪些？",
    ]

    for user_input in conversations:
        print(f"\n用户: {user_input}")
        print("-" * 60)

        try:
            response = agent.chat(user_input, use_rag=True)
            print(f"助手: {response['answer']}")
        except Exception as e:
            print(f"  ❌ 对话失败: {str(e)}")

    # ========== 完成 ==========
    print("\n" + "=" * 80)
    print("✅ 完整工作流演示完成！")
    print("=" * 80)
    print("\n总结:")
    print("1. ✓ 配置加载成功")
    print("2. ✓ 知识库加载成功")
    print("3. ✓ 向量搜索正常")
    print("4. ✓ RAG 问答正常")
    print("5. ✓ Agent 对话正常")
    print("\n下一步:")
    print("- 启动 API 服务: python -m src.api.main")
    print("- 访问 API 文档: http://localhost:8000/docs")
    print("- 查看详细文档: docs/MULTI_DATASOURCE_GUIDE.md")
    print("=" * 80 + "\n")


def main():
    """主函数"""
    try:
        example_complete_workflow()
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

