"""
Vercel Serverless Function 入口
"""
import sys
from pathlib import Path

# 添加 backend 目录到 Python 路径
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.main import app

# Vercel 需要这个 handler
handler = app
