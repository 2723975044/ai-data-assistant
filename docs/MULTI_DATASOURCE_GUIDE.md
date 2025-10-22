# 多数据源知识库使用指南

## 📖 概述

本指南介绍如何配置和使用多数据源知识库功能。该功能允许你：

- 配置多个数据库连接（MySQL、PostgreSQL、MongoDB 等）
- 为每个数据源自动生成独立的知识库
- 通过向量搜索查询数据库结构信息
- 使用 AI 进行智能问答

## 🏗️ 架构说明

```
┌─────────────────┐
│  数据源配置文件  │  config/datasources.yaml
│  (YAML)         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ DataSourceManager│  管理多个数据源配置
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│KnowledgeBaseManager│  管理多个知识库
└────────┬────────┘
         │
         ├──────────┬──────────┬──────────┐
         ▼          ▼          ▼          ▼
    ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
    │  KB 1  │ │  KB 2  │ │  KB 3  │ │  KB N  │
    │(MySQL) │ │(Postgres)│ │(MongoDB)│ │  ...   │
    └────────┘ └────────┘ └────────┘ └────────┘
         │          │          │          │
         └──────────┴──────────┴──────────┘
                     │
                     ▼
            ┌─────────────────┐
            │  Chroma 向量库   │
            │  (多个 Collection)│
            └─────────────────┘
```

## 🚀 快速开始

### 1. 配置环境变量

复制环境变量模板并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填写必要的配置：

```bash
# OpenAI API Key（用于嵌入和 LLM）
OPENAI_API_KEY=your_openai_api_key_here

# MySQL 数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=your_database

# PostgreSQL 数据库配置（如果需要）
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DATABASE=your_database
```

### 2. 配置数据源

编辑 `config/datasources.yaml` 文件，配置你的数据源：

```yaml
datasources:
  # 数据源 1: 公司主数据库
  - name: "company_main_db"
    display_name: "公司主数据库"
    description: "公司核心业务数据库"
    type: "mysql"
    enabled: true
    connection:
      host: "${MYSQL_HOST}"
      port: 3306
      user: "${MYSQL_USER}"
      password: "${MYSQL_PASSWORD}"
      database: "${MYSQL_DATABASE}"
    knowledge_base:
      collection_name: "kb_company_main"
      include_sample_data: true
      sample_data_limit: 5

  # 数据源 2: 分析数据库
  - name: "analytics_db"
    display_name: "数据分析库"
    description: "用于数据分析和报表"
    type: "postgres"
    enabled: true
    connection:
      host: "${POSTGRES_HOST}"
      port: 5432
      user: "${POSTGRES_USER}"
      password: "${POSTGRES_PASSWORD}"
      database: "${POSTGRES_DATABASE}"
    knowledge_base:
      collection_name: "kb_analytics"
      include_sample_data: true
      sample_data_limit: 3
```

### 3. 导入数据源到知识库

使用导入脚本将数据源导入到知识库：

```bash
# 查看所有数据源
python scripts/import_datasources.py --list

# 导入所有启用的数据源
python scripts/import_datasources.py --all

# 导入指定数据源
python scripts/import_datasources.py --datasource company_main_db

# 强制重新导入（覆盖已有数据）
python scripts/import_datasources.py --all --force
```

导入过程会：
1. 连接到数据库
2. 提取表结构信息（表名、字段、类型、注释等）
3. 可选：提取示例数据
4. 将信息转换为文档
5. 使用 Embedding 模型生成向量
6. 存储到 Chroma 向量数据库

### 4. 启动 API 服务

```bash
# 方式 1: 使用 Python
python -m src.api.main

# 方式 2: 使用 uvicorn
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# 方式 3: 使用启动脚本
./start_api.sh  # macOS/Linux
start_api.bat   # Windows
```

服务启动后，访问 http://localhost:8000/docs 查看 API 文档。

## 📡 API 使用

### 1. 获取知识库列表

```bash
curl -X GET "http://localhost:8000/knowledge-bases"
```

响应示例：
```json
{
  "knowledge_bases": [
    {
      "name": "company_main_db",
      "display_name": "公司主数据库",
      "description": "公司核心业务数据库",
      "db_type": "mysql",
      "collection_name": "kb_company_main",
      "is_initialized": true
    }
  ],
  "total": 1
}
```

### 2. 搜索知识库

```bash
# 搜索所有知识库
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "用户表的字段",
    "top_k": 5
  }'

# 搜索指定知识库
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "用户表的字段",
    "knowledge_base": "company_main_db",
    "top_k": 5
  }'
```

### 3. 智能问答

```bash
# 基于知识库的智能问答
curl -X POST "http://localhost:8000/query-kb" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "用户表有哪些字段？每个字段的含义是什么？",
    "knowledge_base": "company_main_db",
    "top_k": 5
  }'
```

响应示例：
```json
{
  "answer": "用户表包含以下字段：\n1. id (INT): 用户唯一标识\n2. username (VARCHAR): 用户名\n3. email (VARCHAR): 邮箱地址\n...",
  "sources": [
    {
      "content": "表名: users\n\n字段信息:\n  - id (INT) [PK]: 用户ID\n  - username (VARCHAR): 用户名\n...",
      "metadata": {
        "source": "database_schema",
        "table_name": "users"
      }
    }
  ],
  "knowledge_base": "company_main_db"
}
```

## 💻 Python 代码使用

### 示例 1: 加载和搜索知识库

```python
from src.utils.datasource_config import get_datasource_manager
from src.vectorstore.knowledge_base_manager import get_knowledge_base_manager
from langchain.embeddings import OpenAIEmbeddings
from src.utils.config import settings

# 创建嵌入模型
embeddings = OpenAIEmbeddings(
    model=settings.embedding_model,
    openai_api_key=settings.openai_api_key
)

# 获取知识库管理器
kb_manager = get_knowledge_base_manager(embedding_model=embeddings)

# 加载所有知识库
kb_manager.load_all()

# 搜索知识库
query = "用户表有哪些字段？"
results = kb_manager.search(query, datasource_name="company_main_db", k=5)

# 打印结果
for kb_name, docs in results.items():
    print(f"\n知识库: {kb_name}")
    for doc in docs:
        print(f"内容: {doc.page_content}")
        print(f"元数据: {doc.metadata}")
```

### 示例 2: 智能问答

```python
from src.rag.rag_retriever import RAGRetriever
from src.llm.llm_factory import LLMFactory

# 获取知识库
kb = kb_manager.get_knowledge_base("company_main_db")

# 创建 LLM
llm = LLMFactory.create_llm(
    provider="openai",
    model_name="gpt-3.5-turbo",
    temperature=0.7
)

# 创建 RAG 检索器
rag_retriever = RAGRetriever(
    vectorstore_manager=kb.vectorstore_manager,
    llm=llm,
    top_k=5
)

# 提问
result = rag_retriever.query(
    question="用户表的结构是什么？",
    return_sources=True
)

print(f"回答: {result['answer']}")
print(f"来源: {result['sources']}")
```

## ⚙️ 高级配置

### 1. 过滤表

在 `datasources.yaml` 中配置要包含或排除的表：

```yaml
knowledge_base:
  collection_name: "kb_company_main"
  # 只包含指定的表
  include_tables: ["users", "orders", "products"]

  # 或者排除某些表
  # exclude_tables: ["logs", "temp_data", "cache"]
```

### 2. 自定义 RAG 参数

在 `datasources.yaml` 中配置 RAG 参数：

```yaml
rag:
  chunk_size: 1000          # 文本块大小
  chunk_overlap: 200        # 文本块重叠大小
  top_k_results: 5          # 返回文档数量
  similarity_threshold: 0.7 # 相似度阈值
```

### 3. 使用不同的向量数据库

```yaml
vector_store:
  type: "faiss"  # 或 "chroma"
  persist_directory: "./data/faiss"
```

## 🔧 故障排查

### 问题 1: 导入失败

**错误**: `配置文件不存在: config/datasources.yaml`

**解决**: 确保配置文件存在，可以从模板复制：
```bash
cp config/datasources.yaml.example config/datasources.yaml
```

### 问题 2: 数据库连接失败

**错误**: `MySQL 连接失败: Access denied`

**解决**:
1. 检查 `.env` 文件中的数据库配置
2. 确保数据库服务正在运行
3. 验证用户名和密码是否正确

### 问题 3: OpenAI API 错误

**错误**: `OpenAI API key not found`

**解决**: 在 `.env` 文件中设置 `OPENAI_API_KEY`

### 问题 4: 知识库未初始化

**错误**: `知识库管理器未初始化`

**解决**: 先运行导入脚本：
```bash
python scripts/import_datasources.py --all
```

## 📚 更多示例

查看 `examples/multi_datasource_example.py` 获取更多使用示例。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📝 License

MIT License

