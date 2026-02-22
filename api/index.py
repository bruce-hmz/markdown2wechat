"""
Vercel Serverless Function 入口
"""
import sys
import os
from pathlib import Path

# 设置项目根目录 - Vercel 部署时文件在 /var/task
project_root = Path(__file__).parent.parent.resolve()
backend_path = project_root / "backend"

# 添加到 Python 路径
sys.path.insert(0, str(backend_path))
sys.path.insert(0, str(project_root))

# 设置环境变量，让 app 知道在 Vercel 环境中
os.environ["VERCEL"] = "1"
os.environ["VERCEL_ROOT"] = str(project_root)

from app.main import app

# Vercel Python runtime 期望的 handler 格式
handler = app
