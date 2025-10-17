"""初始化脚本 - 从数据库创建向量数据库"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.config import settings
from src.utils.logger import log
from src.database.factory import DatabaseFactory
from src.rag.document_processor import DocumentProcessor
from src.vectorstore.vector_store import VectorStoreManager
from langchain.embeddings import OpenAIEmbeddings


def initialize_from_database(
    db_type: str = "mysql",
    db_params: dict = None
):
    """
    从数据库初始化向量数据库
    
    Args:
        db_type: 数据库类型
        db_params: 数据库连接参数
    """
    
    print("=" * 60)
    print("🔧 初始化向量数据库")
    print("=" * 60)
    
    # 1. 连接数据库
    print("\n📊 步骤 1: 连接数据库")
    print("-" * 60)
    
    if db_params is None:
        db_params = {
            'host': settings.mysql_host,
            'port': settings.mysql_port,
            'user': settings.mysql_user,
            'password': settings.mysql_password,
            'database': settings.mysql_database,
        }
    
    db = DatabaseFactory.create_database(db_type, db_params)
    
    with db:
        # 获取数据库结构
        print("✓ 正在获取数据库结构...")
        schema = db.get_schema()
        print(f"✓ 成功获取 {len(schema)} 个表的结构信息")
        
        # 2. 处理文档
        print("\n📝 步骤 2: 处理数据库信息为文档")
        print("-" * 60)
        
        processor = DocumentProcessor(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )
        
        documents = processor.process_database_schema(schema)
        
        # 可选: 添加示例数据
        for table_name in list(schema.keys())[:3]:  # 只取前3个表的示例数据
            try:
                sample_data = db.get_sample_data(table_name, limit=3)
                sample_docs = processor.process_sample_data(table_name, sample_data)
                documents.extend(sample_docs)
            except:
                pass
        
        print(f"✓ 生成了 {len(documents)} 个文档")
        
        # 3. 创建向量数据库
        print("\n🔍 步骤 3: 创建向量数据库")
        print("-" * 60)
        
        embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
        
        vectorstore_manager = VectorStoreManager(
            vector_db_type=settings.vector_db_type,
            embedding_model=embeddings,
            persist_directory=settings.chroma_persist_directory,
            collection_name=settings.collection_name
        )
        
        vectorstore_manager.create_vectorstore(documents)
        
        print("\n" + "=" * 60)
        print("✅ 初始化完成！")
        print("=" * 60)
        print(f"\n向量数据库位置: {settings.chroma_persist_directory}")
        print(f"集合名称: {settings.collection_name}")
        print(f"文档数量: {len(documents)}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="从数据库初始化向量数据库")
    parser.add_argument("--db-type", default="mysql", help="数据库类型")
    
    args = parser.parse_args()
    
    try:
        initialize_from_database(db_type=args.db_type)
    except Exception as e:
        log.error(f"初始化失败: {str(e)}")
        print(f"\n❌ 错误: {str(e)}")
