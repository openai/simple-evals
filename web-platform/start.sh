#!/bin/bash

# Eval Platform 启动脚本

echo "🚀 启动 Eval Platform..."

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 创建数据目录
mkdir -p data/prompt_versions
mkdir -p data/eval_runs

echo "📦 启动服务..."
docker-compose up -d

echo ""
echo "✅ 服务已启动！"
echo ""
echo "🌐 访问地址:"
echo "   前端界面: http://localhost:3000"
echo "   API 文档: http://localhost:8000/docs"
echo "   API 地址: http://localhost:8000"
echo ""
echo "📋 常用命令:"
echo "   查看日志: docker-compose logs -f"
echo "   停止服务: docker-compose down"
echo "   重启服务: docker-compose restart"
echo ""
echo "⚠️  首次启动可能需要几分钟下载镜像，请耐心等待..."
