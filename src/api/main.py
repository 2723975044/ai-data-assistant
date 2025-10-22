"""FastAPI 主应用"""
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.api.models import (
    ChatRequest, ChatResponse,
    QueryRequest, QueryResponse,
    StatusResponse, HistoryResponse,
    MessageResponse
)


# 全局实例
agent_instance = None
kb_manager = None  # 知识库管理器


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global agent_instance, kb_manager
    
    print("🚀 启动 AI 数据助手服务...")
    
    # 尝试加载知识库管理器
    try:
        from src.utils.datasource_config import get_datasource_manager
        from src.vectorstore.knowledge_base_manager import get_knowledge_base_manager
        from langchain.embeddings import OpenAIEmbeddings
        from src.utils.config import settings
    
        # 初始化知识库管理器
        datasource_manager = get_datasource_manager()
        embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
        kb_manager = get_knowledge_base_manager(
            datasource_manager=datasource_manager,
            embedding_model=embeddings
        )

        # 尝试加载已有的知识库
        kb_manager.load_all()
        print("✓ 知识库管理器已初始化")

    except Exception as e:
        print(f"⚠️  知识库管理器初始化失败: {str(e)}")
        print("⚠️  请先配置数据源并导入数据")

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


# ========== 知识库相关接口 ==========

@app.get("/knowledge-bases", response_model=KnowledgeBaseListResponse)
async def list_knowledge_bases():
    """获取所有知识库列表"""
    global kb_manager

    if kb_manager is None:
        raise HTTPException(
            status_code=503,
            detail="知识库管理器未初始化"
        )

    try:
        kb_list = []
        for name, kb in kb_manager.knowledge_bases.items():
            kb_info = KnowledgeBaseInfo(
                name=name,
                display_name=kb.datasource_config.display_name,
                description=kb.datasource_config.description,
                db_type=kb.datasource_config.type,
                collection_name=kb.datasource_config.get_collection_name(),
                is_initialized=kb.is_initialized
            )
            kb_list.append(kb_info)

        return KnowledgeBaseListResponse(
            knowledge_bases=kb_list,
            total=len(kb_list)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取知识库列表失败: {str(e)}")


@app.post("/search", response_model=SearchResponse)
async def search_knowledge_bases(request: SearchRequest):
    """
    搜索知识库

    Args:
        request: 搜索请求

    Returns:
        搜索结果
    """
    global kb_manager

    if kb_manager is None:
        raise HTTPException(
            status_code=503,
            detail="知识库管理器未初始化"
        )

    try:
        # 执行搜索
        search_results = kb_manager.search(
            query=request.query,
            datasource_name=request.knowledge_base,
            k=request.top_k
        )

        # 格式化结果
        formatted_results = {}
        total_count = 0

        for kb_name, docs in search_results.items():
            formatted_docs = []
            for doc in docs:
                formatted_docs.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata
                })
            formatted_results[kb_name] = formatted_docs
            total_count += len(docs)

        return SearchResponse(
            results=formatted_results,
            total_results=total_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@app.post("/query-kb", response_model=QueryResponse)
async def query_knowledge_base(request: QueryRequest):
    """
    基于知识库的智能问答

    Args:
        request: 查询请求

    Returns:
        查询响应
    """
    global kb_manager

    if kb_manager is None:
        raise HTTPException(
            status_code=503,
            detail="知识库管理器未初始化"
        )

    try:
        from src.rag.rag_retriever import RAGRetriever, create_database_qa_prompt
        from src.llm.llm_factory import LLMFactory
        from src.utils.config import settings

        # 获取知识库
        if request.knowledge_base:
            kb = kb_manager.get_knowledge_base(request.knowledge_base)
            if not kb:
                raise HTTPException(
                    status_code=404,
                    detail=f"知识库不存在: {request.knowledge_base}"
                )
            kb_name = request.knowledge_base
        else:
            # 使用第一个可用的知识库
            if not kb_manager.knowledge_bases:
                raise HTTPException(
                    status_code=404,
                    detail="没有可用的知识库"
                )
            kb_name = list(kb_manager.knowledge_bases.keys())[0]
            kb = kb_manager.knowledge_bases[kb_name]

        # 创建 LLM
        llm = LLMFactory.create_llm(
            provider=settings.default_llm_provider,
            model_name=settings.default_model_name,
            temperature=settings.default_temperature
        )

        # 创建 RAG 检索器
        rag_retriever = RAGRetriever(
            vectorstore_manager=kb.vectorstore_manager,
            llm=llm,
            top_k=request.top_k
        )

        # 执行查询
        result = rag_retriever.query(
            question=request.query,
            return_sources=True
        )

        return QueryResponse(
            answer=result["answer"],
            sources=result.get("sources"),
            knowledge_base=kb_name
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
