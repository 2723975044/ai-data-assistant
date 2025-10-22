# AI 数据助手 - 基于 LangChain 的智能数据管理系统

## 📖 项目简介

这是一个基于 LangChain 框架开发的 AI 智能数据助手，通过 RAG（检索增强生成）技术结合向量数据库，为公司数据管理提供智能化的查询和分析服务。

### 核心功能

- 🤖 **智能对话**: 通过自然语言与数据库交互
- 📊 **多数据源支持**: 支持配置多个数据库（MySQL、PostgreSQL、MongoDB 等）
- 📚 **多知识库管理**: 为每个数据源自动生成独立的知识库
- 🔍 **RAG 检索**: 基于向量相似度的智能检索
- 💾 **向量存储**: 支持 Chroma、FAISS 等向量数据库
- 🧠 **多模型支持**: 集成 OpenAI、通义千问、智谱 AI 等多种大模型
- 📡 **API 服务**: 提供 RESTful API 接口
- 🔧 **灵活配置**: 通过 YAML 配置文件管理数据源

## 🏗️ 项目架构

```
ai-data-assistant/
├── src/                    # 源代码目录
│   ├── agent/             # AI Agent 核心逻辑
│   ├── database/          # 数据库连接模块
│   ├── vectorstore/       # 向量数据库模块
│   ├── llm/               # 大模型集成
│   ├── rag/               # RAG 检索引擎
│   ├── api/               # API 服务层
│   └── utils/             # 工具函数
├── tests/                 # 测试代码
├── config/                # 配置文件
├── data/                  # 数据存储
├── logs/                  # 日志文件
├── requirements.txt       # 依赖包
├── .env.example          # 环境变量模板
└── README.md             # 项目文档
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
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

# 编辑 .env 文件，填入你的 API Keys 和数据库配置
```

### 3. 配置数据源

编辑 `config/datasources.yaml` 文件，配置你的数据库连接：

```yaml
datasources:
  - name: "company_main_db"
    display_name: "公司主数据库"
    type: "mysql"
    enabled: true
    connection:
      host: "${MYSQL_HOST}"
      database: "${MYSQL_DATABASE}"
      # ... 其他配置
```

### 4. 导入数据源到知识库

```bash
# 查看所有数据源
python scripts/import_datasources.py --list

# 导入所有启用的数据源
python scripts/import_datasources.py --all

# 导入指定数据源
python scripts/import_datasources.py --datasource company_main_db
```

### 5. 启动 API 服务

```bash
# 启动 API 服务
python -m src.api.main

# 或使用 uvicorn
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/docs 查看 API 文档

### 6. 测试使用

```bash
# 运行多数据源示例
python examples/multi_datasource_example.py

# 或运行基础示例
python examples/basic_usage.py
```

## 📚 使用文档

### 详细文档

- [多数据源知识库使用指南](docs/MULTI_DATASOURCE_GUIDE.md) - 完整的配置和使用教程
- [API 文档](http://localhost:8000/docs) - 启动服务后访问

### 支持的数据库

- MySQL
- PostgreSQL
- MongoDB
- SQLite
- Redis

### 支持的 LLM 模型

- OpenAI (GPT-3.5, GPT-4)
- 阿里云通义千问
- 智谱 AI (ChatGLM)
- Anthropic Claude

### 支持的向量数据库

- ChromaDB (默认)
- FAISS

## 🎯 主要特性

### 1. 多数据源配置

通过 `config/datasources.yaml` 配置多个数据源：

```yaml
datasources:
  - name: "company_main_db"
    display_name: "公司主数据库"
    type: "mysql"
    enabled: true
    knowledge_base:
      collection_name: "kb_company_main"
```

### 2. 自动知识库生成

系统会自动：
- 提取数据库表结构
- 提取字段信息和注释
- 可选提取示例数据
- 生成向量索引

### 3. 智能查询

支持多种查询方式：
- 搜索所有知识库
- 搜索指定知识库
- 基于知识库的智能问答

### 4. RESTful API

提供完整的 API 接口：
- `GET /knowledge-bases` - 获取知识库列表
- `POST /search` - 搜索知识库
- `POST /query-kb` - 智能问答

## 🛠️ 开发指南

### 运行测试

```bash
pytest tests/
```

### 代码格式化

```bash
black src/
flake8 src/
```

## 📝 License

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
