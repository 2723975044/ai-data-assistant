"""FastAPI 主应用"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.api.models import (
    ChatRequest, ChatResponse,
    QueryRequest, QueryResponse,
    StatusResponse, HistoryResponse,
    MessageResponse
)


# 全局 Agent 实例
agent_instance = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global agent_instance
    
    print("🚀 启动 AI 数据助手服务...")
    
    # 这里可以初始化 Agent
    # 注意: 实际使用时需要先配置好环境变量和数据库
    print("⚠️  Agent 未初始化，请先调用 /init 接口进行初始化")
    
    yield
    
    print("👋 关闭 AI 数据助手服务...")


# 创建 FastAPI 应用
app = FastAPI(
    title="AI 数据助手 API",
    description="基于 LangChain 的智能数据管理系统",
    version="0.1.0",
    lifespan=lifespan
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=MessageResponse)
async def root():
    """根路径"""
    return MessageResponse(
        message="欢迎使用 AI 数据助手 API！请访问 /docs 查看 API 文档"
    )


@app.get("/health", response_model=MessageResponse)
async def health_check():
    """健康检查"""
    return MessageResponse(message="服务运行正常")


@app.post("/init", response_model=MessageResponse)
async def initialize_agent():
    """
    初始化 Agent
    
    注意: 这是一个示例接口，实际使用时需要根据具体情况配置
    """
    global agent_instance
    
    try:
        # 这里应该初始化 Agent
        # 由于需要数据库连接等配置，这里仅作示例
        
        return MessageResponse(
            message="Agent 初始化需要配置数据库连接和 API Keys，请参考文档进行配置"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"初始化失败: {str(e)}")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    与 Agent 对话
    
    Args:
        request: 聊天请求
        
    Returns:
        聊天响应
    """
    global agent_instance
    
    if agent_instance is None:
        raise HTTPException(
            status_code=400,
            detail="Agent 未初始化，请先调用 /init 接口"
        )
    
    try:
        result = agent_instance.chat(
            user_input=request.message,
            use_rag=request.use_rag
        )
        
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"对话失败: {str(e)}")


@app.post("/query", response_model=QueryResponse)
async def query_database(request: QueryRequest):
    """
    查询数据库信息
    
    Args:
        request: 查询请求
        
    Returns:
        查询响应
    """
    global agent_instance
    
    if agent_instance is None:
        raise HTTPException(
            status_code=400,
            detail="Agent 未初始化，请先调用 /init 接口"
        )
    
    try:
        result = agent_instance.query_database(request.query)
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@app.get("/status", response_model=StatusResponse)
async def get_status():
    """获取 Agent 状态"""
    global agent_instance
    
    if agent_instance is None:
        raise HTTPException(
            status_code=400,
            detail="Agent 未初始化，请先调用 /init 接口"
        )
    
    try:
        status = agent_instance.get_status()
        return StatusResponse(**status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取状态失败: {str(e)}")


@app.get("/history", response_model=HistoryResponse)
async def get_history():
    """获取对话历史"""
    global agent_instance
    
    if agent_instance is None:
        raise HTTPException(
            status_code=400,
            detail="Agent 未初始化，请先调用 /init 接口"
        )
    
    try:
        history = agent_instance.get_conversation_history()
        return HistoryResponse(history=history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史失败: {str(e)}")


@app.post("/clear", response_model=MessageResponse)
async def clear_history():
    """清空对话历史"""
    global agent_instance
    
    if agent_instance is None:
        raise HTTPException(
            status_code=400,
            detail="Agent 未初始化，请先调用 /init 接口"
        )
    
    try:
        agent_instance.clear_history()
        return MessageResponse(message="对话历史已清空")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空历史失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
