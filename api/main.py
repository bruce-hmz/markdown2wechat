"""
微信公众号 Markdown 工具 - FastAPI 应用入口 (Vercel 版本)
"""

import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

# 创建 FastAPI 应用
app = FastAPI(
    title="Markdown 转微信公众号格式工具",
    description="将 Markdown 文章转换为可以直接粘贴到微信公众号编辑器的富文本格式",
    version="1.0.0"
)

# CORS 中间件（允许跨域）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 目录配置
BASE_DIR = Path(__file__).resolve().parent  # api/
THEMES_DIR = BASE_DIR / "themes"
STATIC_DIR = BASE_DIR / "static"

# 挂载静态文件
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# 导入路由
from api.app.routers import markdown, themes, images

# 注册路由
app.include_router(markdown.router)
app.include_router(themes.router)
app.include_router(images.router)


@app.get("/")
async def index():
    """主页面"""
    index_file = BASE_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return HTMLResponse(content="<h1>Markdown2WeChat</h1><p>Frontend not found</p>")


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "themes_dir": str(THEMES_DIR)}
