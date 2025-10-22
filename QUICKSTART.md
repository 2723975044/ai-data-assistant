# 快速开始指南

## 🎯 5 分钟快速上手

### 前置要求

- Python 3.8+
- 数据库（MySQL/PostgreSQL/MongoDB 任选其一）
- OpenAI API Key

### 步骤 1: 克隆并安装

```bash
# 进入项目目录
cd ai-data-assistant

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 步骤 2: 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件
nano .env  # 或使用你喜欢的编辑器
```

**必填配置：**
```bash
OPENAI_API_KEY=sk-your-openai-api-key-here

# 如果使用 MySQL
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=your_database
```

### 步骤 3: 配置数据源

编辑 `config/datasources.yaml`：

```yaml
datasources:
  - name: "my_database"
    display_name: "我的数据库"
    description: "主数据库"
    type: "mysql"  # 或 postgres, mongodb
    enabled: true
    connection:
      host: "${MYSQL_HOST}"
      port: 3306
      user: "${MYSQL_USER}"
      password: "${MYSQL_PASSWORD}"
      database: "${MYSQL_DATABASE}"
    knowledge_base:
      collection_name: "kb_my_database"
      include_sample_data: true
      sample_data_limit: 5
```

### 步骤 4: 验证配置

```bash
# 运行配置检查
python scripts/check_config.py
```

### 步骤 5: 导入数据源

```bash
# 导入所有数据源到知识库
python scripts/import_datasources.py --all

# 或导入指定数据源
python scripts/import_datasources.py --datasource my_database
```

### 步骤 6: 启动服务

```bash
# 启动 API 服务
python -m src.api.main

# 或使用 uvicorn（推荐开发环境）
uvicorn src.api.main:app --reload
```

访问 http://localhost:8000/docs 查看 API 文档

### 步骤 7: 测试使用

#### 方式 1: 使用 API

```bash
# 获取知识库列表
curl http://localhost:8000/knowledge-bases

# 搜索知识库
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "用户表有哪些字段", "top_k": 5}'

# 智能问答
curl -X POST http://localhost:8000/query-kb \
  -H "Content-Type: application/json" \
  -d '{"query": "数据库中有哪些表？", "top_k": 5}'
```

#### 方式 2: 使用 Python 示例

```bash
# 运行完整工作流示例
python examples/complete_workflow_example.py

# 运行 API 客户端示例
python examples/api_client_example.py

# 运行多数据源示例
python examples/multi_datasource_example.py
```

## 🚀 使用 Makefile（推荐）

如果你的系统支持 `make`，可以使用更简单的命令：

```bash
# 查看所有可用命令
make help

# 初始化项目
make init

# 检查配置
make check

# 导入所有数据源
make import-all

# 启动服务
make run

# 运行示例
make example
```

## 🚀 一键启动（最简单）

```bash
# 使用快速启动脚本
./scripts/quick_start.sh
```

这个脚本会自动：
1. 检查 Python 环境
2. 创建虚拟环境
3. 安装依赖
4. 检查配置
5. 导入数据源
6. 启动服务

## ���� 常用命令速查

| 命令 | 说明 |
|------|------|
| `make check` | 检查配置 |
| `make import-all` | 导入所有数据源 |
| `make list` | 列出所有数据源 |
| `make run` | 启动 API 服务 |
| `make dev` | 开发模式启动 |
| `make example` | 运行完整示例 |
| `make clean` | 清理临时文件 |
| `make test` | 运行测试 |

## 🔧 常见问题

### 1. 导入失败：找不到配置文件

**问题：** `FileNotFoundError: 配置文件不存在`

**解决：** 确保 `config/datasources.yaml` 文件存在

```bash
# 检查文件是否存在
ls config/datasources.yaml
```

### 2. 数据库连接失败

**问题：** `ConnectionError: MySQL 连接失败`

**解决：**
1. 检查数据库服务是否运行
2. 验证 `.env` 中的数据库配置
3. 测试数据库连接：

```bash
# MySQL
mysql -h localhost -u root -p

# PostgreSQL
psql -h localhost -U postgres
```

### 3. OpenAI API 错误

**问题：** `OpenAI API key not found`

**解决：** 在 `.env` 文件中设置 `OPENAI_API_KEY`

```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 4. 知识库未初始化

**问题：** `知识库管理器未初始化`

**解决：** 先运行导入脚本

```bash
python scripts/import_datasources.py --all
```

### 5. 端口被占用

**问题：** `Address already in use`

**解决：** 更改端口或停止占用端口的进程

```bash
# 查找占用 8000 端口的进程
lsof -i :8000

# 或使用其他端口
uvicorn src.api.main:app --port 8001
```

## 📖 下一步

- 📘 阅读[完整文档](docs/MULTI_DATASOURCE_GUIDE.md)
- 🔍 查看 [API 文档](http://localhost:8000/docs)
- 💻 查看[示例代码](examples/)
- 📋 查看 [TODO 列表](TODO.md)

## 🆘 获取帮助

- 查看文档：`docs/` 目录
- 运行配置检查：`python scripts/check_config.py`
- 查看日志：`logs/app.log`
- 提交 Issue

## 🎉 成功标志

如果你看到以下输出，说明一切正常：

```
✓ 知识库管理器已初始化
✓ 已加载 X 个知识库
INFO:     Uvicorn running on http://0.0.0.0:8000
```

现在你可以：
- 访问 http://localhost:8000/docs 查看 API 文档
- 使用 API 进行查询
- 运行示例代码
- 开始开发你的应用

祝使用愉快！🚀

