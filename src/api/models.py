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


class QueryResponse(BaseModel):
    """查询响应"""
    answer: str = Field(..., description="查询答案")
    sources: Optional[List[Dict[str, Any]]] = Field(None, description="来源文档")


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
