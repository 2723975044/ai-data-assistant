"""API 数据模型"""
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., description="用户消息", min_length=1)
    use_rag: bool = Field(True, description="是否使用 RAG 检索")
    session_id: Optional[str] = Field(None, description="会话 ID")


class ChatResponse(BaseModel):
    """聊天响应"""
    answer: str = Field(..., description="助手回答")
    user_input: str = Field(..., description="用户输入")
    agent_name: str = Field(..., description="Agent 名称")
    use_rag: bool = Field(..., description="是否使用了 RAG")
    rag_sources: Optional[List[Dict[str, Any]]] = Field(None, description="RAG 来源")
    error: Optional[str] = Field(None, description="错误信息")


class QueryRequest(BaseModel):
    """查询请求"""
    query: str = Field(..., description="查询问题", min_length=1)
    knowledge_base: Optional[str] = Field(None, description="指定知识库名称（数据源名称），不指定则搜索所有知识库")
    top_k: int = Field(5, description="返回文档数量", ge=1, le=20)


class QueryResponse(BaseModel):
    """查询响应"""
    answer: str = Field(..., description="查询答案")
    sources: Optional[List[Dict[str, Any]]] = Field(None, description="来源文档")
    knowledge_base: Optional[str] = Field(None, description="使用的知识库名称")


class StatusResponse(BaseModel):
    """状态响应"""
    agent_name: str
    agent_description: str
    conversation_count: int
    max_history: int
    vectorstore_type: str


class HistoryResponse(BaseModel):
    """历史记录响应"""
    history: List[Dict[str, str]]


class MessageResponse(BaseModel):
    """消息响应"""
    message: str
    success: bool = True


class KnowledgeBaseInfo(BaseModel):
    """知识库信息"""
    name: str = Field(..., description="数据源名称")
    display_name: str = Field(..., description="显示名称")
    description: str = Field(..., description="描述")
    db_type: str = Field(..., description="数据库类型")
    collection_name: str = Field(..., description="向量集合名称")
    is_initialized: bool = Field(..., description="是否已初始化")


class KnowledgeBaseListResponse(BaseModel):
    """知识库列表响应"""
    knowledge_bases: List[KnowledgeBaseInfo] = Field(..., description="知识库列表")
    total: int = Field(..., description="总数")


class SearchRequest(BaseModel):
    """搜索请求"""
    query: str = Field(..., description="搜索查询", min_length=1)
    knowledge_base: Optional[str] = Field(None, description="指定知识库名称，不指定则搜索所有")
    top_k: int = Field(5, description="返回文档数量", ge=1, le=20)


class SearchResponse(BaseModel):
    """搜索响应"""
    results: Dict[str, List[Dict[str, Any]]] = Field(..., description="搜索结果，按知识库分组")
    total_results: int = Field(..., description="总结果数")
