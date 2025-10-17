"""配置管理模块"""
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用配置"""
    
    # ========== LLM Settings ==========
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    openai_api_base: str = Field("https://api.openai.com/v1", env="OPENAI_API_BASE")
    dashscope_api_key: Optional[str] = Field(None, env="DASHSCOPE_API_KEY")
    zhipuai_api_key: Optional[str] = Field(None, env="ZHIPUAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    
    default_llm_provider: str = Field("openai", env="DEFAULT_LLM_PROVIDER")
    default_model_name: str = Field("gpt-3.5-turbo", env="DEFAULT_MODEL_NAME")
    default_temperature: float = Field(0.7, env="DEFAULT_TEMPERATURE")
    default_max_tokens: int = Field(2000, env="DEFAULT_MAX_TOKENS")
    
    # ========== Embedding Settings ==========
    embedding_model: str = Field("text-embedding-ada-002", env="EMBEDDING_MODEL")
    
    # ========== Vector Database Settings ==========
    vector_db_type: str = Field("chroma", env="VECTOR_DB_TYPE")
    chroma_persist_directory: str = Field("./data/chroma", env="CHROMA_PERSIST_DIRECTORY")
    collection_name: str = Field("company_data", env="COLLECTION_NAME")
    
    # ========== Database Connections ==========
    # MySQL
    mysql_host: str = Field("localhost", env="MYSQL_HOST")
    mysql_port: int = Field(3306, env="MYSQL_PORT")
    mysql_user: str = Field("", env="MYSQL_USER")
    mysql_password: str = Field("", env="MYSQL_PASSWORD")
    mysql_database: str = Field("", env="MYSQL_DATABASE")
    
    # PostgreSQL
    postgres_host: str = Field("localhost", env="POSTGRES_HOST")
    postgres_port: int = Field(5432, env="POSTGRES_PORT")
    postgres_user: str = Field("", env="POSTGRES_USER")
    postgres_password: str = Field("", env="POSTGRES_PASSWORD")
    postgres_database: str = Field("", env="POSTGRES_DATABASE")
    
    # MongoDB
    mongodb_uri: str = Field("mongodb://localhost:27017/", env="MONGODB_URI")
    mongodb_database: str = Field("", env="MONGODB_DATABASE")
    
    # Redis
    redis_host: str = Field("localhost", env="REDIS_HOST")
    redis_port: int = Field(6379, env="REDIS_PORT")
    redis_password: str = Field("", env="REDIS_PASSWORD")
    redis_db: int = Field(0, env="REDIS_DB")
    
    # ========== RAG Settings ==========
    chunk_size: int = Field(1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(200, env="CHUNK_OVERLAP")
    top_k_results: int = Field(5, env="TOP_K_RESULTS")
    similarity_threshold: float = Field(0.7, env="SIMILARITY_THRESHOLD")
    
    # ========== API Settings ==========
    api_host: str = Field("0.0.0.0", env="API_HOST")
    api_port: int = Field(8000, env="API_PORT")
    api_reload: bool = Field(True, env="API_RELOAD")
    
    # ========== Logging ==========
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: str = Field("./logs/app.log", env="LOG_FILE")
    
    # ========== Agent Settings ==========
    agent_name: str = Field("数据小秘书", env="AGENT_NAME")
    agent_description: str = Field(
        "我是你的数据管理助手，可以帮你查询和分析公司数据",
        env="AGENT_DESCRIPTION"
    )
    max_conversation_history: int = Field(10, env="MAX_CONVERSATION_HISTORY")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 全局配置实例
settings = Settings()
