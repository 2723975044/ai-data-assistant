.PHONY: help install check import-all import clean test run dev docs

# 默认目标
help:
	@echo "AI 数据助手 - 可用命令:"
	@echo ""
	@echo "  make install      - 安装依赖包"
	@echo "  make check        - 检查配置"
	@echo "  make import-all   - 导入所有数据源"
	@echo "  make import DS=name - 导入指定数据源"
	@echo "  make clean        - 清理临时文件"
	@echo "  make test         - 运行测试"
	@echo "  make run          - 启动 API 服务"
	@echo "  make dev          - 开发模式启动"
	@echo "  make docs         - 生成文档"
	@echo "  make example      - 运行完整示例"
	@echo "  make api-example  - 运行 API 客户端示例"
	@echo ""

# 安装依赖
install:
	@echo "安装依赖包..."
	pip install -r requirements.txt
	@echo "✓ 依赖包安装完成"

# 检查配置
check:
	@echo "检查配置..."
	python scripts/check_config.py

# 导入所有数据源
import-all:
	@echo "导入所有数据源..."
	python scripts/import_datasources.py --all

# 导入指定数据源
import:
	@echo "导入数据源: $(DS)"
	python scripts/import_datasources.py --datasource $(DS)

# 列出数据源
list:
	@echo "数据源列表:"
	python scripts/import_datasources.py --list

# 清理临时文件
clean:
	@echo "清理临时文件..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	@echo "✓ 清理完成"

# 运行测试
test:
	@echo "运行测试..."
	pytest tests/ -v

# 启动 API 服务
run:
	@echo "启动 API 服务..."
	@echo "访问 http://localhost:8000/docs 查看 API 文档"
	python -m src.api.main

# 开发模式
dev:
	@echo "开发模式启动..."
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# 生成文档
docs:
	@echo "生成文档..."
	@echo "文档位置: docs/"

# 运行完整示例
example:
	@echo "运行完整工作流示例..."
	python examples/complete_workflow_example.py

# 运行 API 客户端示例
api-example:
	@echo "运行 API 客户端示例..."
	python examples/api_client_example.py

# 运行多数据源示例
multi-example:
	@echo "运行多数据源示例..."
	python examples/multi_datasource_example.py

# 格式化代码
format:
	@echo "格式化代码..."
	black src/ examples/ scripts/
	@echo "✓ 代码格式化完成"

# 代码检查
lint:
	@echo "代码检查..."
	flake8 src/ --max-line-length=100
	@echo "✓ 代码检查完成"

# 创建 .env 文件
init-env:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✓ .env 文件已创建，请编辑填写配置"; \
	else \
		echo "⚠️  .env 文件已存在"; \
	fi

# 完整初始化
init: init-env install check
	@echo ""
	@echo "=================================="
	@echo "✅ 初始化完成！"
	@echo "=================================="
	@echo ""
	@echo "下一步:"
	@echo "1. 编辑 .env 文件，填写 API Keys 和数据库配置"
	@echo "2. 编辑 config/datasources.yaml，配置数据源"
	@echo "3. 运行 make import-all 导入数据源"
	@echo "4. 运行 make run 启动服务"
	@echo ""

# 快速开始
quick-start:
	@echo "快速开始..."
	./scripts/quick_start.sh

