# 项目结构

```
ai-data-assistant/
├── src/                          # 源代码目录
│   ├── __init__.py
│   ├── agent/                    # Agent 模块
│   │   ├── __init__.py
│   │   └── data_assistant.py    # 数据助手 Agent 核心逻辑
│   ├── api/                      # API 服务模块
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI 主应用
│   │   └── models.py            # API 数据模型
│   ├── database/                 # 数据库模块
│   │   ├── __init__.py
│   │   ├── base.py              # 数据库基类
│   │   ├── mysql_db.py          # MySQL 连接
│   │   ├── postgres_db.py       # PostgreSQL 和 MongoDB 连接
│   │   └── factory.py           # 数据库工厂
│   ├── llm/                      # LLM 模块
│   │   ├── __init__.py
│   │   └── llm_factory.py       # LLM 工厂类
│   ├── rag/                      # RAG 检索模块
│   │   ├── __init__.py
│   │   ├── document_processor.py # 文档处理
│   │   └── rag_retriever.py     # RAG 检索引擎
│   ├── vectorstore/              # 向量数据库模块
│   │   ├── __init__.py
│   │   └── vector_store.py      # 向量存储管理
│   └── utils/                    # 工具模块
│       ├── __init__.py
│       ├── config.py            # 配置管理
│       └── logger.py            # 日志配置
│
├── examples/                     # 示例代码
│   ├── basic_usage.py           # 基础使用示例
│   ├── quick_start.py           # 快速开始示例
│   └── init_vectorstore.py      # 初始化向量数据库脚本
│
├── tests/                        # 测试代码
│   └── (待添加)
│
├── config/                       # 配置文件目录
│   └── (可选的额外配置)
│
├── data/                         # 数据存储目录
│   └── chroma/                  # ChromaDB 数据
│
├── logs/                         # 日志目录
│   └── app.log
│
├── requirements.txt              # Python 依赖
├── .env.example                 # 环境变量模板
├── .env                         # 环境变量配置（不提交到 git）
├── .gitignore                   # Git 忽略文件
├── README.md                    # 项目说明
├── USAGE.md                     # 使用指南
├── ARCHITECTURE.md              # 架构说明
├── start_api.sh                # Linux/macOS 启动脚本
└── start_api.bat               # Windows 启动脚本
```

## 目录说明

### src/ - 源代码
所有的核心业务逻辑代码

#### agent/ - AI Agent
- `data_assistant.py`: 数据助手的主要逻辑，包括对话管理、RAG 集成

#### api/ - Web API
- `main.py`: FastAPI 应用主文件，定义所有 API 端点
- `models.py`: Pydantic 数据模型，用于请求/响应验证

#### database/ - 数据库连接
- `base.py`: 数据库基类，定义统一接口
- `mysql_db.py`: MySQL 数据库实现
- `postgres_db.py`: PostgreSQL 和 MongoDB 实现
- `factory.py`: 工厂模式创建数据库实例

#### llm/ - 大语言模型
- `llm_factory.py`: 统一的 LLM 创建接口，支持多种模型

#### rag/ - 检索增强生成
- `document_processor.py`: 文档处理和分块
- `rag_retriever.py`: RAG 检索和问答

#### vectorstore/ - 向量数据库
- `vector_store.py`: 向量数据库管理，支持多种向量数据库

#### utils/ - 工具函数
- `config.py`: 配置管理，使用 Pydantic Settings
- `logger.py`: 日志配置，使用 loguru

### examples/ - 示例代码
提供不同场景的使用示例

- `basic_usage.py`: 完整功能演示
- `quick_start.py`: 快速开始，使用模拟数据
- `init_vectorstore.py`: 从数据库初始化向量数据库

### tests/ - 测试代码
单元测试和集成测试（待完善）

### data/ - 数据目录
存储向量数据库等持久化数据

### logs/ - 日志目录
应用运行日志

## 文件说明

### 配置文件
- `requirements.txt`: Python 依赖包列表
- `.env.example`: 环境变量模板
- `.env`: 实际的环境变量配置（需要自己创建）
- `.gitignore`: Git 忽略规则

### 文档
- `README.md`: 项目介绍和快速开始
- `USAGE.md`: 详细使用指南
- `ARCHITECTURE.md`: 架构设计文档

### 启动脚本
- `start_api.sh`: Linux/macOS 启动脚本
- `start_api.bat`: Windows 启动脚本

## 模块依赖关系

```
API Layer (api/)
    ↓
Agent Layer (agent/)
    ↓
RAG Layer (rag/)
    ↓
┌─────────────┬──────────────┬─────────────┐
│             │              │             │
Vector Store  LLM           Database     Utils
(vectorstore/) (llm/)       (database/)  (utils/)
```

## 配置优先级

1. 运行时参数（最高优先级）
2. 环境变量（`.env` 文件）
3. 默认配置（代码中的默认值）

## 扩展建议

### 添加新功能
1. 在对应模块下创建新文件
2. 实现功能逻辑
3. 在 `__init__.py` 中导出
4. 编写测试

### 添加新的 API 端点
1. 在 `src/api/models.py` 定义数据模型
2. 在 `src/api/main.py` 添加路由
3. 实现业务逻辑

### 添加新的数据库支持
1. 在 `src/database/` 创建新的连接器
2. 继承 `BaseDatabase` 类
3. 在 `factory.py` 中注册

### 添加新的 LLM 支持
1. 在 `src/llm/llm_factory.py` 添加创建方法
2. 处理相应的配置
