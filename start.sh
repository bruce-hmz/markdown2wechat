#!/bin/bash

# Markdown 转微信公众号工具启动脚本

echo "启动 Markdown 转微信公众号工具..."

# 进入 backend 目录
cd "$(dirname "$0")/backend"

# 检查是否安装了依赖
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "首次运行，正在安装依赖..."
    pip install -r requirements.txt
fi

# 启动应用
echo "正在启动应用..."
echo "访问地址: http://localhost:8000"
echo ""
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
