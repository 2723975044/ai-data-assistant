"""RAG 检索引擎"""
from typing import List, Optional, Dict, Any
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate


class RAGRetriever:
    """RAG 检索引擎"""
    
    def __init__(
        self,
        vectorstore_manager,
        llm,
        top_k: int = 5,
        similarity_threshold: float = 0.7
    ):
        """
        初始化 RAG 检索引擎
        
        Args:
            vectorstore_manager: 向量数据库管理器
            llm: 大语言模型
            top_k: 返回文档数量
            similarity_threshold: 相似度阈值
        """
        self.vectorstore_manager = vectorstore_manager
        self.llm = llm
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        
        # 创建检索器
        self.retriever = self.vectorstore_manager.as_retriever(
            search_kwargs={"k": top_k}
        )
    
    def retrieve_relevant_docs(self, query: str) -> List[Document]:
        """
        检索相关文档
        
        Args:
            query: 查询文本
            
        Returns:
            相关文档列表
        """
        docs = self.vectorstore_manager.similarity_search(
            query=query,
            k=self.top_k,
            score_threshold=self.similarity_threshold
        )
        
        return docs
    
    def create_qa_chain(
        self,
        chain_type: str = "stuff",
        custom_prompt: Optional[PromptTemplate] = None
    ):
        """
        创建问答链
        
        Args:
            chain_type: 链类型 (stuff, map_reduce, refine, map_rerank)
            custom_prompt: 自定义提示词模板
            
        Returns:
            QA Chain
        """
        chain_kwargs = {}
        
        if custom_prompt:
            chain_kwargs["prompt"] = custom_prompt
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type=chain_type,
            retriever=self.retriever,
            return_source_documents=True,
            chain_type_kwargs=chain_kwargs
        )
        
        return qa_chain
    
    def query(
        self,
        question: str,
        return_sources: bool = True
    ) -> Dict[str, Any]:
        """
        执行查询
        
        Args:
            question: 问题
            return_sources: 是否返回来源文档
            
        Returns:
            查询结果
        """
        # 创建默认的问答链
        qa_chain = self.create_qa_chain()
        
        # 执行查询
        result = qa_chain({"query": question})
        
        response = {
            "answer": result["result"],
        }
        
        if return_sources:
            response["sources"] = [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in result.get("source_documents", [])
            ]
        
        return response


def create_database_qa_prompt() -> PromptTemplate:
    """
    创建数据库问答提示词模板
    
    Returns:
        PromptTemplate
    """
    template = """你是一个专业的数据库查询助手。基于以下数据库信息回答用户的问题。

数据库信息:
{context}

用户问题: {question}

请根据上述数据库信息给出专业、准确的回答。如果信息不足以回答问题，请明确说明。

回答:"""
    
    return PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )
