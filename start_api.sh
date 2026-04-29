#!/bin/bash

# Keyword Recognition API启动脚本

echo "============================================================"
echo "关键词识别API服务启动"
echo "============================================================"

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "错误: 虚拟环境不存在，请先运行: uv sync"
    exit 1
fi

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "警告: .env文件不存在"
    echo "请从.env.example复制并配置API密钥:"
    echo "cp .env.example .env"
    echo "然后编辑.env文件，设置ZHIPU_API_KEY"
fi

# 启动API服务
echo "启动API服务..."
echo "API地址: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo "按 Ctrl+C 停止服务"
echo "============================================================"

uv run uvicorn semantic_toolkit.api:app --host 0.0.0.0 --port 8000 --reload
