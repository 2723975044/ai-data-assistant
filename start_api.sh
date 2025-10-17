#!/bin/bash

# 启动 API 服务脚本

echo "🚀 启动 AI 数据助手 API 服务..."
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "⚠️  未找到虚拟环境，正在创建..."
    python -m venv venv
fi

# 激活虚拟环境
echo "📦 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📥 安装依赖包..."
pip install -r requirements.txt

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️  未找到 .env 文件，正在复制模板..."
    cp .env.example .env
    echo "❗ 请先编辑 .env 文件配置 API Keys 和数据库信息"
    exit 1
fi

# 创建必要的目录
echo "📁 创建数据目录..."
mkdir -p data/chroma
mkdir -p logs

# 启动服务
echo ""
echo "=" * 60
echo "✅ 准备就绪！正在启动服务..."
echo "=" * 60
echo ""
echo "📍 API 文档: http://localhost:8000/docs"
echo "📍 健康检查: http://localhost:8000/health"
echo ""

uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
