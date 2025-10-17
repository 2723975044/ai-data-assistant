"""快速开始示例 - 不需要数据库"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from langchain.schema import Document
from src.utils.config import settings
from src.llm.llm_factory import LLMFactory
from src.vectorstore.vector_store import VectorStoreManager
from src.rag.rag_retriever import RAGRetriever
from src.agent.data_assistant import DataAssistantAgent


def main():
    """快速开始示例 - 使用模拟数据"""
    
    print("=" * 60)
    print("🚀 AI 数据助手 - 快速开始示例")
    print("=" * 60)
    
    # 1. 创建模拟的数据库文档
    print("\n📝 创建模拟数据...")
    
    mock_documents = [
        Document(
            page_content="""
            表名: users (用户表)
            
            字段信息:
              - id (INT) [PRIMARY KEY]: 用户ID
              - username (VARCHAR) [NOT NULL]: 用户名
              - email (VARCHAR) [NOT NULL]: 邮箱地址
              - created_at (DATETIME): 创建时间
              - status (TINYINT): 用户状态 (0-禁用, 1-启用)
            """,
            metadata={"source": "mock_db", "table": "users"}
        ),
        Document(
            page_content="""
            表名: orders (订单表)
            
            字段信息:
              - id (INT) [PRIMARY KEY]: 订单ID
              - user_id (INT) [FOREIGN KEY]: 用户ID
              - total_amount (DECIMAL): 订单总金额
              - status (VARCHAR): 订单状态 (pending, paid, shipped, completed)
              - created_at (DATETIME): 创建时间
            """,
            metadata={"source": "mock_db", "table": "orders"}
        ),
        Document(
            page_content="""
            表名: products (产品表)
            
            字段信息:
              - id (INT) [PRIMARY KEY]: 产品ID
              - name (VARCHAR) [NOT NULL]: 产品名称
              - price (DECIMAL): 产品价格
              - stock (INT): 库存数量
              - category (VARCHAR): 产品分类
              - description (TEXT): 产品描述
            """,
            metadata={"source": "mock_db", "table": "products"}
        ),
    ]
    
    print(f"✓ 创建了 {len(mock_documents)} 个模拟文档")
    
    try:
        # 2. 创建 LLM（确保已配置 API Key）
        print("\n🧠 初始化 LLM...")
        
        llm = LLMFactory.create_llm(
            provider="openai",  # 可改为 dashscope, zhipuai 等
            model_name="gpt-3.5-turbo",
            temperature=0.7,
            api_key=settings.openai_api_key
        )
        print("✓ LLM 初始化成功")
        
        # 3. 创建向量数据库
        print("\n🔍 创建向量数据库...")
        
        from langchain.embeddings import OpenAIEmbeddings
        
        embeddings = OpenAIEmbeddings(openai_api_key=settings.openai_api_key)
        
        vectorstore_manager = VectorStoreManager(
            vector_db_type="chroma",
            embedding_model=embeddings,
            persist_directory="./data/quick_start_chroma",
            collection_name="quick_start"
        )
        
        vectorstore_manager.create_vectorstore(mock_documents)
        print("✓ 向量数据库创建成功")
        
        # 4. 创建 RAG 检索器
        print("\n🔗 创建 RAG 检索器...")
        
        rag_retriever = RAGRetriever(
            vectorstore_manager=vectorstore_manager,
            llm=llm,
            top_k=3
        )
        print("✓ RAG 检索器创建成功")
        
        # 5. 创建 Agent
        print("\n🤖 创建数据助手...")
        
        agent = DataAssistantAgent(
            llm=llm,
            vectorstore_manager=vectorstore_manager,
            rag_retriever=rag_retriever,
            agent_name="数据小秘书",
            agent_description="我是你的数据管理助手，可以帮你查询和分析公司数据"
        )
        print("✓ 数据助手创建成功")
        
        # 6. 开始交互式对话
        print("\n" + "=" * 60)
        print("💬 开始对话（输入 'quit' 或 'exit' 退出）")
        print("=" * 60)
        
        while True:
            try:
                user_input = input("\n你: ").strip()
                
                if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                    print("\n👋 再见！")
                    break
                
                if not user_input:
                    continue
                
                # 与 Agent 对话
                response = agent.chat(user_input, use_rag=True)
                
                print(f"\n{agent.agent_name}: {response['answer']}")
                
                # 显示来源（可选）
                if response.get('rag_sources'):
                    print(f"\n📚 [参考了 {len(response['rag_sources'])} 个数据源]")
                
            except KeyboardInterrupt:
                print("\n\n👋 再见！")
                break
            except Exception as e:
                print(f"\n❌ 错误: {str(e)}")
        
    except Exception as e:
        print(f"\n❌ 初始化失败: {str(e)}")
        print("\n💡 提示:")
        print("1. 请确保已配置 .env 文件")
        print("2. 请确保已设置 OPENAI_API_KEY 或其他 LLM API Key")
        print("3. 运行: cp .env.example .env 并编辑配置")


if __name__ == "__main__":
    main()
