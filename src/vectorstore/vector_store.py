"""向量数据库管理"""
from typing import List, Optional, Any
from langchain.vectorstores import Chroma, FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings.base import Embeddings
from langchain.schema import Document


class VectorStoreManager:
    """向量数据库管理器"""
    
    def __init__(
        self,
        vector_db_type: str = "chroma",
        embedding_model: Optional[Embeddings] = None,
        persist_directory: Optional[str] = None,
        collection_name: str = "default"
    ):
        """
        初始化向量数据库管理器
        
        Args:
            vector_db_type: 向量数据库类型 (chroma, faiss)
            embedding_model: 嵌入模型
            persist_directory: 持久化目录
            collection_name: 集合名称
        """
        self.vector_db_type = vector_db_type.lower()
        self.embedding_model = embedding_model or OpenAIEmbeddings()
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.vectorstore = None
    
    def create_vectorstore(self, documents: List[Document]) -> Any:
        """
        创建向量数据库
        
        Args:
            documents: 文档列表
            
        Returns:
            向量数据库实例
        """
        if self.vector_db_type == "chroma":
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embedding_model,
                persist_directory=self.persist_directory,
                collection_name=self.collection_name
            )
            
            if self.persist_directory:
                self.vectorstore.persist()
                print(f"✓ Chroma 向量数据库已创建并持久化到: {self.persist_directory}")
            
        elif self.vector_db_type == "faiss":
            self.vectorstore = FAISS.from_documents(
                documents=documents,
                embedding=self.embedding_model
            )
            
            if self.persist_directory:
                self.vectorstore.save_local(self.persist_directory)
                print(f"✓ FAISS 向量数据库已保存到: {self.persist_directory}")
        
        else:
            raise ValueError(f"不支持的向量数据库类型: {self.vector_db_type}")
        
        return self.vectorstore
    
    def load_vectorstore(self) -> Any:
        """
        加载已有的向量数据库
        
        Returns:
            向量数据库实例
        """
        if not self.persist_directory:
            raise ValueError("未指定持久化目录，无法加载向量数据库")
        
        if self.vector_db_type == "chroma":
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embedding_model,
                collection_name=self.collection_name
            )
            print(f"✓ 已加载 Chroma 向量数据库: {self.persist_directory}")
            
        elif self.vector_db_type == "faiss":
            self.vectorstore = FAISS.load_local(
                self.persist_directory,
                self.embedding_model
            )
            print(f"✓ 已加载 FAISS 向量数据库: {self.persist_directory}")
        
        return self.vectorstore
    
    def add_documents(self, documents: List[Document]) -> None:
        """
        添加文档到向量数据库
        
        Args:
            documents: 文档列表
        """
        if not self.vectorstore:
            raise ValueError("向量数据库未初始化，请先创建或加载")
        
        self.vectorstore.add_documents(documents)
        
        # 持久化
        if self.persist_directory:
            if self.vector_db_type == "chroma":
                self.vectorstore.persist()
            elif self.vector_db_type == "faiss":
                self.vectorstore.save_local(self.persist_directory)
        
        print(f"✓ 已添加 {len(documents)} 个文档到向量数据库")
    
    def similarity_search(
        self,
        query: str,
        k: int = 5,
        score_threshold: Optional[float] = None
    ) -> List[Document]:
        """
        相似度搜索
        
        Args:
            query: 查询文本
            k: 返回文档数量
            score_threshold: 相似度阈值
            
        Returns:
            相关文档列表
        """
        if not self.vectorstore:
            raise ValueError("向量数据库未初始化，请先创建或加载")
        
        if score_threshold is not None:
            # 使用相似度阈值过滤
            docs_and_scores = self.vectorstore.similarity_search_with_score(query, k=k)
            docs = [doc for doc, score in docs_and_scores if score >= score_threshold]
        else:
            docs = self.vectorstore.similarity_search(query, k=k)
        
        return docs
    
    def as_retriever(self, **kwargs):
        """
        转换为检索器
        
        Returns:
            Retriever 对象
        """
        if not self.vectorstore:
            raise ValueError("向量数据库未初始化，请先创建或加载")
        
        return self.vectorstore.as_retriever(**kwargs)
    
    def delete_collection(self) -> None:
        """删除集合"""
        if self.vectorstore and self.vector_db_type == "chroma":
            self.vectorstore.delete_collection()
            print(f"✓ 已删除集合: {self.collection_name}")


def get_vectorstore_from_config(config, documents: Optional[List[Document]] = None):
    """
    从配置创建向量数据库管理器
    
    Args:
        config: 配置对象
        documents: 初始文档列表
        
    Returns:
        向量数据库管理器实例
    """
    from langchain.embeddings import OpenAIEmbeddings
    
    # 创建嵌入模型
    embeddings = OpenAIEmbeddings(
        model=config.embedding_model,
        openai_api_key=config.openai_api_key
    )
    
    # 创建向量数据库管理器
    manager = VectorStoreManager(
        vector_db_type=config.vector_db_type,
        embedding_model=embeddings,
        persist_directory=config.chroma_persist_directory,
        collection_name=config.collection_name
    )
    
    # 如果提供了文档，创建向量数据库
    if documents:
        manager.create_vectorstore(documents)
    else:
        # 尝试加载已有数据库
        try:
            manager.load_vectorstore()
        except Exception:
            print("⚠️  未找到已有向量数据库，需要先添加文档")
    
    return manager
