#!/bin/bash
# 快速开始脚本 - 一键配置和启动

set -e

echo "=================================="
echo "🚀 AI 数据助手 - 快速开始"
echo "=================================="

# 检查 Python 版本
echo ""
echo "检查 Python 版本..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "✓ Python 版本: $python_version"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo ""
    echo "创建虚拟环境..."
    python -m venv venv
    echo "✓ 虚拟环境已创建"
fi

# 激活虚拟环境
echo ""
echo "激活虚拟环境..."
source venv/bin/activate
echo "✓ 虚拟环境已激活"

# 安装依赖
echo ""
echo "安装依赖包..."
pip install -r requirements.txt -q
echo "✓ 依赖包已安装"

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  .env 文件不存在"
    if [ -f ".env.example" ]; then
        echo "复制 .env.example 为 .env..."
        cp .env.example .env
        echo "✓ .env 文件已创建"
        echo ""
        echo "⚠️  请编辑 .env 文件，填写必要的配置："
        echo "   - OPENAI_API_KEY"
        echo "   - 数据库连接信息"
        echo ""
        read -p "按 Enter 继续编辑 .env 文件..."
        ${EDITOR:-nano} .env
    fi
else
    echo ""
    echo "✓ .env 文件已存在"
fi

# 检查配置文件
if [ ! -f "config/datasources.yaml" ]; then
    echo ""
    echo "⚠️  config/datasources.yaml 不存在"
    echo "请先配置数据源"
    exit 1
fi

# 创建必要的目录
echo ""
echo "创建必要的目录..."
mkdir -p data/chroma
mkdir -p logs
echo "✓ 目录已创建"

# 运行配置检查
echo ""
echo "=================================="
echo "运行配置检查..."
echo "=================================="
python scripts/check_config.py

# 询问是否导入数据源
echo ""
read -p "是否导入数据源到知识库？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "=================================="
    echo "导入数据源..."
    echo "=================================="
    python scripts/import_datasources.py --all
fi

# 询问是否启动 API 服务
echo ""
read -p "是否启动 API 服务？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "=================================="
    echo "启动 API 服务..."
    echo "=================================="
    echo "访问 http://localhost:8000/docs 查看 API 文档"
    echo "按 Ctrl+C 停止服务"
    echo ""
    python -m src.api.main
else
    echo ""
    echo "=================================="
    echo "✅ 配置完成！"
    echo "=================================="
    echo ""
    echo "下一步："
    echo "1. 启动 API 服务:"
    echo "   python -m src.api.main"
    echo ""
    echo "2. 运行示例:"
    echo "   python examples/complete_workflow_example.py"
    echo ""
    echo "3. 查看文档:"
    echo "   docs/MULTI_DATASOURCE_GUIDE.md"
    echo ""
fi

