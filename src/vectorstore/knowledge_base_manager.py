"""知识库管理模块 - 支持多数据源的知识库管理"""
from pathlib import Path
from typing import Dict, List, Optional, Any

from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings.base import Embeddings
from langchain.schema import Document

from .vector_store import VectorStoreManager
from ..database.factory import DatabaseFactory
from ..rag.document_processor import DocumentProcessor
from ..utils.datasource_config import DataSourceConfig, DataSourceManager


class KnowledgeBase:
    """单个知识库"""

    def __init__(
        self,
        datasource_config: DataSourceConfig,
        vectorstore_manager: VectorStoreManager,
        document_processor: DocumentProcessor
    ):
        """
        初始化知识库

        Args:
            datasource_config: 数据源配置
            vectorstore_manager: 向量数据库管理器
            document_processor: 文档处理器
        """
        self.datasource_config = datasource_config
        self.vectorstore_manager = vectorstore_manager
        self.document_processor = document_processor
        self.is_initialized = False

    def initialize(self) -> None:
        """初始化知识库 - 从数据源导入数据"""
        print(f"\n{'='*60}")
        print(f"🔧 初始化知识库: {self.datasource_config.display_name}")
        print(f"{'='*60}")

        # 1. 连接数据库
        print(f"\n📊 步骤 1: 连接数据库 ({self.datasource_config.type})")
        print("-" * 60)

        db = DatabaseFactory.create_database(
            self.datasource_config.type,
            self.datasource_config.connection
        )

        documents = []

        with db:
            # 2. 获取数据库结构
            print("✓ 正在获取数据库结构...")
            schema = db.get_schema()

            # 过滤表
            filtered_schema = self._filter_tables(schema)
            print(f"✓ 成功获取 {len(filtered_schema)} 个表的结构信息")

            # 3. 处理文档
            print(f"\n📝 步骤 2: 处理数据库信息为文档")
            print("-" * 60)

            # 处理 schema
            schema_docs = self.document_processor.process_database_schema(filtered_schema)
            documents.extend(schema_docs)
            print(f"✓ 生成了 {len(schema_docs)} 个 schema 文档")

            # 4. 可选：添加示例数据
            if self.datasource_config.should_include_sample_data():
                print(f"\n📋 步骤 3: 添加示例数据")
                print("-" * 60)

                sample_limit = self.datasource_config.get_sample_data_limit()
                sample_count = 0

                for table_name in list(filtered_schema.keys()):
                    try:
                        sample_data = db.get_sample_data(table_name, limit=sample_limit)
                        if sample_data:
                            sample_docs = self.document_processor.process_sample_data(
                                table_name, sample_data
                            )
                            documents.extend(sample_docs)
                            sample_count += len(sample_docs)
                    except Exception as e:
                        print(f"⚠️  获取表 {table_name} 的示例数据失败: {str(e)}")

                print(f"✓ 生成了 {sample_count} 个示例数据文档")

        # 5. 创建向量数据库
        print(f"\n🔍 步骤 4: 创建向量数据库")
        print("-" * 60)

        self.vectorstore_manager.create_vectorstore(documents)
        self.is_initialized = True

        print(f"\n{'='*60}")
        print(f"✅ 知识库初始化完成！")
        print(f"{'='*60}")
        print(f"数据源: {self.datasource_config.display_name}")
        print(f"集合名称: {self.datasource_config.get_collection_name()}")
        print(f"文档总数: {len(documents)}")
        print(f"{'='*60}\n")

    def _filter_tables(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据配置过滤表

        Args:
            schema: 完整的数据库 schema

        Returns:
            过滤后的 schema
        """
        include_tables = self.datasource_config.get_include_tables()
        exclude_tables = self.datasource_config.get_exclude_tables()

        if include_tables:
            # 只包含指定的表
            return {k: v for k, v in schema.items() if k in include_tables}
        elif exclude_tables:
            # 排除指定的表
            return {k: v for k, v in schema.items() if k not in exclude_tables}
        else:
            # 包含所有表
            return schema

    def load(self) -> None:
        """加载已有的知识库"""
        self.vectorstore_manager.load_vectorstore()
        self.is_initialized = True
        print(f"✓ 已加载知识库: {self.datasource_config.display_name}")

    def add_documents(self, documents: List[Document]) -> None:
        """添加文档到知识库"""
        if not self.is_initialized:
            raise ValueError("知识库未初始化，请先调用 initialize() 或 load()")

        self.vectorstore_manager.add_documents(documents)

    def search(self, query: str, k: int = 5) -> List[Document]:
        """搜索知识库"""
        if not self.is_initialized:
            raise ValueError("知识库未初始化，请先调用 initialize() 或 load()")

        return self.vectorstore_manager.similarity_search(query, k=k)

    def get_retriever(self, **kwargs):
        """获取检索器"""
        if not self.is_initialized:
            raise ValueError("知识库未初始化，请先调用 initialize() 或 load()")

        return self.vectorstore_manager.as_retriever(**kwargs)


class KnowledgeBaseManager:
    """知识库管理器 - 管理多个数据源的知识库"""

    def __init__(
        self,
        datasource_manager: DataSourceManager,
        embedding_model: Optional[Embeddings] = None,
        vector_db_type: str = "chroma",
        persist_directory: str = "./data/chroma"
    ):
        """
        初始化知识库管理器

        Args:
            datasource_manager: 数据源管理器
            embedding_model: 嵌入模型
            vector_db_type: 向量数据库类型
            persist_directory: 持久化目录
        """
        self.datasource_manager = datasource_manager
        self.embedding_model = embedding_model or OpenAIEmbeddings()
        self.vector_db_type = vector_db_type
        self.persist_directory = Path(persist_directory)

        # 知识库字典: datasource_name -> KnowledgeBase
        self.knowledge_bases: Dict[str, KnowledgeBase] = {}

        # 文档处理器
        rag_config = datasource_manager.get_rag_config()
        self.document_processor = DocumentProcessor(
            chunk_size=rag_config.get('chunk_size', 1000),
            chunk_overlap=rag_config.get('chunk_overlap', 200)
        )

    def initialize_all(self, force: bool = False) -> None:
        """
        初始化所有启用的数据源的知识库

        Args:
            force: 是否强制重新初始化（即使已存在）
        """
        print("\n" + "=" * 80)
        print("🚀 开始初始化所有知识库")
        print("=" * 80)

        enabled_datasources = self.datasource_manager.get_enabled_datasources()

        if not enabled_datasources:
            print("⚠️  没有启用的数据源")
            return

        print(f"\n找到 {len(enabled_datasources)} 个启用的数据源\n")

        for datasource in enabled_datasources:
            try:
                self.initialize_knowledge_base(datasource.name, force=force)
            except Exception as e:
                print(f"❌ 初始化知识库 {datasource.name} 失败: {str(e)}")
                import traceback
                traceback.print_exc()
                continue

        print("\n" + "=" * 80)
        print(f"✅ 知识库初始化完成！共 {len(self.knowledge_bases)} 个知识库")
        print("=" * 80 + "\n")

    def initialize_knowledge_base(self, datasource_name: str, force: bool = False) -> KnowledgeBase:
        """
        初始化指定数据源的知识库

        Args:
            datasource_name: 数据源名称
            force: 是否强制重新初始化

        Returns:
            知识库实例
        """
        # 获取数据源配置
        datasource_config = self.datasource_manager.get_datasource_by_name(datasource_name)
        if not datasource_config:
            raise ValueError(f"数据源不存在: {datasource_name}")

        if not datasource_config.enabled:
            raise ValueError(f"数据源未启用: {datasource_name}")

        # 检查是否已存在
        if datasource_name in self.knowledge_bases and not force:
            print(f"⚠️  知识库 {datasource_name} 已存在，跳过初始化")
            return self.knowledge_bases[datasource_name]

        # 创建向量数据库管理器
        vectorstore_manager = VectorStoreManager(
            vector_db_type=self.vector_db_type,
            embedding_model=self.embedding_model,
            persist_directory=str(self.persist_directory),
            collection_name=datasource_config.get_collection_name()
        )

        # 创建知识库
        kb = KnowledgeBase(
            datasource_config=datasource_config,
            vectorstore_manager=vectorstore_manager,
            document_processor=self.document_processor
        )

        # 初始化知识库
        kb.initialize()

        # 保存到字典
        self.knowledge_bases[datasource_name] = kb

        return kb

    def load_knowledge_base(self, datasource_name: str) -> KnowledgeBase:
        """
        加载已有的知识库

        Args:
            datasource_name: 数据源名称

        Returns:
            知识库实例
        """
        # 获取数据源配置
        datasource_config = self.datasource_manager.get_datasource_by_name(datasource_name)
        if not datasource_config:
            raise ValueError(f"数据源不存在: {datasource_name}")

        # 检查是否已加载
        if datasource_name in self.knowledge_bases:
            return self.knowledge_bases[datasource_name]

        # 创建向量数据库管理器
        vectorstore_manager = VectorStoreManager(
            vector_db_type=self.vector_db_type,
            embedding_model=self.embedding_model,
            persist_directory=str(self.persist_directory),
            collection_name=datasource_config.get_collection_name()
        )

        # 创建知识库
        kb = KnowledgeBase(
            datasource_config=datasource_config,
            vectorstore_manager=vectorstore_manager,
            document_processor=self.document_processor
        )

        # 加载知识库
        kb.load()

        # 保存到字典
        self.knowledge_bases[datasource_name] = kb

        return kb

    def load_all(self) -> None:
        """加载所有启用的知识库"""
        print("\n" + "=" * 80)
        print("📂 加载所有知识库")
        print("=" * 80 + "\n")

        enabled_datasources = self.datasource_manager.get_enabled_datasources()

        for datasource in enabled_datasources:
            try:
                self.load_knowledge_base(datasource.name)
            except Exception as e:
                print(f"⚠️  加载知识库 {datasource.name} 失败: {str(e)}")
                continue

        print(f"\n✅ 成功加载 {len(self.knowledge_bases)} 个知识库\n")

    def get_knowledge_base(self, datasource_name: str) -> Optional[KnowledgeBase]:
        """
        获取知识库实例

        Args:
            datasource_name: 数据源名称

        Returns:
            知识库实例，如果不存在返回 None
        """
        return self.knowledge_bases.get(datasource_name)

    def search(
        self,
        query: str,
        datasource_name: Optional[str] = None,
        k: int = 5
    ) -> Dict[str, List[Document]]:
        """
        搜索知识库

        Args:
            query: 查询文本
            datasource_name: 数据源名称，如果为 None 则搜索所有知识库
            k: 每个知识库返回的文档数量

        Returns:
            搜索结果字典: datasource_name -> documents
        """
        results = {}

        if datasource_name:
            # 搜索指定知识库
            kb = self.get_knowledge_base(datasource_name)
            if kb:
                results[datasource_name] = kb.search(query, k=k)
            else:
                raise ValueError(f"知识库不存在: {datasource_name}")
        else:
            # 搜索所有知识库
            for name, kb in self.knowledge_bases.items():
                try:
                    results[name] = kb.search(query, k=k)
                except Exception as e:
                    print(f"⚠️  搜索知识库 {name} 失败: {str(e)}")
                    continue

        return results

    def list_knowledge_bases(self) -> None:
        """列出所有知识库"""
        print("\n" + "=" * 80)
        print("📚 知识库列表")
        print("=" * 80)

        if not self.knowledge_bases:
            print("\n暂无已加载的知识库\n")
            return

        for i, (name, kb) in enumerate(self.knowledge_bases.items(), 1):
            status = "✓ 已初始化" if kb.is_initialized else "✗ 未初始化"
            print(f"\n{i}. {kb.datasource_config.display_name}")
            print(f"   数据源名称: {name}")
            print(f"   数据库类型: {kb.datasource_config.type}")
            print(f"   集合名称: {kb.datasource_config.get_collection_name()}")
            print(f"   状态: {status}")

        print("\n" + "=" * 80 + "\n")


def get_knowledge_base_manager(
    datasource_manager: Optional[DataSourceManager] = None,
    embedding_model: Optional[Embeddings] = None
) -> KnowledgeBaseManager:
    """
    创建知识库管理器

    Args:
        datasource_manager: 数据源管理器
        embedding_model: 嵌入模型

    Returns:
        知识库管理器实例
    """
    from ..utils.datasource_config import get_datasource_manager

    if datasource_manager is None:
        datasource_manager = get_datasource_manager()

    vector_config = datasource_manager.get_vector_store_config()

    return KnowledgeBaseManager(
        datasource_manager=datasource_manager,
        embedding_model=embedding_model,
        vector_db_type=vector_config.get('type', 'chroma'),
        persist_directory=vector_config.get('persist_directory', './data/chroma')
    )

