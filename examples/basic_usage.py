"""基础使用示例"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.config import settings
from src.utils.logger import log
from src.database.factory import DatabaseFactory
from src.llm.llm_factory import get_llm_from_config
from src.rag.document_processor import DocumentProcessor
from src.vectorstore.vector_store import get_vectorstore_from_config
from src.rag.rag_retriever import RAGRetriever
from src.agent.data_assistant import DataAssistantAgent


def main():
    """主函数"""
    
    print("=" * 60)
    print("🤖 AI 数据助手 - 基础使用示例")
    print("=" * 60)
    
    # 1. 连接数据库（示例）
    print("\n📊 步骤 1: 连接数据库")
    print("-" * 60)
    
    try:
        # 配置数据库连接参数
        db_params = {
            'host': settings.mysql_host,
            'port': settings.mysql_port,
            'user': settings.mysql_user,
            'password': settings.mysql_password,
            'database': settings.mysql_database,
        }
        
        # 创建数据库连接
        db = DatabaseFactory.create_database('mysql', db_params)
        
        # 连接数据库
        with db:
            # 获取数据库结构
            print("✓ 正在获取数据库结构...")
            schema = db.get_schema()
            print(f"✓ 成功获取 {len(schema)} 个表的结构信息")
            
            # 2. 处理数据库信息为文档
            print("\n📝 步骤 2: 处理数据库信息")
            print("-" * 60)
            
            processor = DocumentProcessor(
                chunk_size=settings.chunk_size,
                chunk_overlap=settings.chunk_overlap
            )
            
            # 将数据库结构转换为文档
            documents = processor.process_database_schema(schema)
            print(f"✓ 生成了 {len(documents)} 个文档")
            
            # 3. 创建向量数据库
            print("\n🔍 步骤 3: 创建向量数据库")
            print("-" * 60)
            
            vectorstore_manager = get_vectorstore_from_config(settings, documents)
            print("✓ 向量数据库创建成功")
            
            # 4. 初始化 LLM
            print("\n🧠 步骤 4: 初始化大语言模型")
            print("-" * 60)
            
            llm = get_llm_from_config(settings)
            print(f"✓ 使用模型: {settings.default_model_name}")
            
            # 5. 创建 RAG 检索器
            print("\n🔗 步骤 5: 创建 RAG 检索器")
            print("-" * 60)
            
            rag_retriever = RAGRetriever(
                vectorstore_manager=vectorstore_manager,
                llm=llm,
                top_k=settings.top_k_results,
                similarity_threshold=settings.similarity_threshold
            )
            print("✓ RAG 检索器创建成功")
            
            # 6. 创建 Agent
            print("\n🤖 步骤 6: 创建数据助手 Agent")
            print("-" * 60)
            
            agent = DataAssistantAgent(
                llm=llm,
                vectorstore_manager=vectorstore_manager,
                rag_retriever=rag_retriever,
                agent_name=settings.agent_name,
                agent_description=settings.agent_description,
                max_history=settings.max_conversation_history
            )
            print(f"✓ Agent '{settings.agent_name}' 创建成功")
            
            # 7. 测试对话
            print("\n💬 步骤 7: 测试对话功能")
            print("=" * 60)
            
            # 测试问题列表
            test_questions = [
                "介绍一下数据库中有哪些表？",
                "用户表的结构是什么样的？",
                "如何查询所有用户的信息？"
            ]
            
            for i, question in enumerate(test_questions, 1):
                print(f"\n问题 {i}: {question}")
                print("-" * 60)
                
                response = agent.chat(question, use_rag=True)
                
                print(f"\n{settings.agent_name}: {response['answer']}")
                
                if response.get('rag_sources'):
                    print(f"\n📚 参考来源: {len(response['rag_sources'])} 个文档")
            
            # 8. 显示对话历史
            print("\n📜 对话历史")
            print("=" * 60)
            
            history = agent.get_conversation_history()
            print(f"总共 {len(history)} 条对话记录")
            
            # 9. 显示 Agent 状态
            print("\n📊 Agent 状态")
            print("=" * 60)
            
            status = agent.get_status()
            for key, value in status.items():
                print(f"{key}: {value}")
            
            print("\n" + "=" * 60)
            print("✅ 示例运行完成！")
            print("=" * 60)
            
    except Exception as e:
        log.error(f"运行出错: {str(e)}")
        print(f"\n❌ 错误: {str(e)}")
        print("\n💡 提示:")
        print("1. 请确保已配置 .env 文件")
        print("2. 请确保数据库连接信息正确")
        print("3. 请确保已配置 OpenAI API Key 或其他 LLM API Key")


if __name__ == "__main__":
    main()
