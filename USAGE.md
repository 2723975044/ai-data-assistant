# 使用指南

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，至少需要配置以下内容：
# - OPENAI_API_KEY (或其他 LLM 的 API Key)
# - 数据库连接信息（如果需要连接真实数据库）
```

### 3. 运行示例

#### 方式 1: 快速开始（无需数据库）

```bash
python examples/quick_start.py
```

这个示例使用模拟数据，可以直接体验对话功能。

#### 方式 2: 连接真实数据库

1. 首先初始化向量数据库：

```bash
python examples/init_vectorstore.py
```

2. 然后运行完整示例：

```bash
python examples/basic_usage.py
```

#### 方式 3: 启动 API 服务

```bash
# 方式 1: 使用 Python
python -m src.api.main

# 方式 2: 使用 uvicorn
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

访问 API 文档: http://localhost:8000/docs

## 详细配置说明

### LLM 配置

支持以下大模型:

#### OpenAI
```env
OPENAI_API_KEY=your-api-key
DEFAULT_LLM_PROVIDER=openai
DEFAULT_MODEL_NAME=gpt-3.5-turbo
```

#### 阿里云通义千问
```env
DASHSCOPE_API_KEY=your-api-key
DEFAULT_LLM_PROVIDER=dashscope
DEFAULT_MODEL_NAME=qwen-turbo
```

#### 智谱 AI
```env
ZHIPUAI_API_KEY=your-api-key
DEFAULT_LLM_PROVIDER=zhipuai
DEFAULT_MODEL_NAME=chatglm_turbo
```

### 数据库配置

#### MySQL
```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your-username
MYSQL_PASSWORD=your-password
MYSQL_DATABASE=your-database
```

#### PostgreSQL
```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=your-username
POSTGRES_PASSWORD=your-password
POSTGRES_DATABASE=your-database
```

#### MongoDB
```env
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=your-database
```

### 向量数据库配置

```env
# 使用 ChromaDB（推荐）
VECTOR_DB_TYPE=chroma
CHROMA_PERSIST_DIRECTORY=./data/chroma
COLLECTION_NAME=company_data

# 或使用 FAISS
VECTOR_DB_TYPE=faiss
```

## API 使用示例

### 1. 对话接口

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "介绍一下数据库中有哪些表？",
    "use_rag": true
  }'
```

### 2. 查询接口

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "用户表的结构是什么？"
  }'
```

### 3. 获取状态

```bash
curl -X GET "http://localhost:8000/status"
```

### 4. 获取对话历史

```bash
curl -X GET "http://localhost:8000/history"
```

### 5. 清空对话历史

```bash
curl -X POST "http://localhost:8000/clear"
```

## 代码集成示例

### 基础使用

```python
from src.utils.config import settings
from src.llm.llm_factory import LLMFactory
from src.vectorstore.vector_store import VectorStoreManager
from src.rag.rag_retriever import RAGRetriever
from src.agent.data_assistant import DataAssistantAgent
from langchain.schema import Document

# 1. 创建 LLM
llm = LLMFactory.create_llm(
    provider="openai",
    model_name="gpt-3.5-turbo",
    api_key="your-api-key"
)

# 2. 准备文档
documents = [
    Document(page_content="你的文档内容", metadata={"source": "db"})
]

# 3. 创建向量数据库
vectorstore = VectorStoreManager(
    vector_db_type="chroma",
    persist_directory="./data/chroma"
)
vectorstore.create_vectorstore(documents)

# 4. 创建 RAG 检索器
rag = RAGRetriever(
    vectorstore_manager=vectorstore,
    llm=llm
)

# 5. 创建 Agent
agent = DataAssistantAgent(
    llm=llm,
    vectorstore_manager=vectorstore,
    rag_retriever=rag
)

# 6. 开始对话
response = agent.chat("你好，介绍一下自己")
print(response['answer'])
```

### 连接数据库

```python
from src.database.factory import DatabaseFactory
from src.rag.document_processor import DocumentProcessor

# 连接数据库
db_params = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'password',
    'database': 'mydb'
}

db = DatabaseFactory.create_database('mysql', db_params)

with db:
    # 获取数据库结构
    schema = db.get_schema()
    
    # 处理为文档
    processor = DocumentProcessor()
    documents = processor.process_database_schema(schema)
    
    # 后续步骤同上...
```

## 常见问题

### 1. LangChain 导入错误

这是正常的 linting 警告，因为还没有安装依赖。运行以下命令安装：

```bash
pip install -r requirements.txt
```

### 2. 数据库连接失败

- 检查数据库是否运行
- 检查连接参数是否正确
- 检查网络连接

### 3. API Key 错误

- 确保已在 .env 文件中配置正确的 API Key
- 检查 API Key 是否有效

### 4. 向量数据库初始化失败

- 确保有写入权限
- 检查 persist_directory 路径是否存在

## 高级功能

### 自定义 Prompt

```python
from langchain.prompts import PromptTemplate

custom_prompt = PromptTemplate(
    template="你是一个专业的数据分析师...\n{context}\n{question}",
    input_variables=["context", "question"]
)

qa_chain = rag_retriever.create_qa_chain(custom_prompt=custom_prompt)
```

### 添加新文档

```python
from langchain.schema import Document

new_docs = [
    Document(page_content="新的文档内容", metadata={"source": "new"})
]

vectorstore_manager.add_documents(new_docs)
```

### 切换 LLM

```python
# 切换到阿里云通义千问
llm = LLMFactory.create_llm(
    provider="dashscope",
    model_name="qwen-turbo",
    api_key="your-dashscope-key"
)

# 重新创建 Agent
agent = DataAssistantAgent(
    llm=llm,
    vectorstore_manager=vectorstore_manager,
    rag_retriever=rag_retriever
)
```

## 性能优化建议

1. **使用本地 Embedding 模型**（避免 API 调用）
2. **调整 chunk_size 和 chunk_overlap**
3. **使用 FAISS 替代 Chroma**（更快的检索）
4. **缓存常见查询结果**
5. **限制对话历史长度**

## 部署建议

### Docker 部署

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 使用 Gunicorn

```bash
pip install gunicorn
gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker
```
