"""
微信公众号 Markdown 工具 - FastAPI 应用入口 (Vercel 版本)
"""

import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
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

# 主题目录 - Vercel 环境下在 api/themes
BASE_DIR = Path(__file__).resolve().parent  # api/
THEMES_DIR = BASE_DIR / "themes"

# 导入路由
from api.app.routers import markdown, themes, images

# 注册路由
app.include_router(markdown.router)
app.include_router(themes.router)
app.include_router(images.router)


@app.get("/")
async def index():
    """主页面 - 返回提示信息"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>Markdown2WeChat API</title>
        <style>
            body { font-family: -apple-system, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            h1 { color: #333; }
            code { background: #f5f5f5; padding: 2px 6px; border-radius: 4px; }
            .endpoint { margin: 10px 0; padding: 10px; background: #f9f9f9; border-radius: 8px; }
        </style>
    </head>
    <body>
        <h1>Markdown2WeChat API</h1>
        <p>欢迎使用 Markdown 转微信公众号格式工具 API</p>

        <h2>可用接口</h2>
        <div class="endpoint">
            <code>POST /api/convert</code> - 转换 Markdown 为微信 HTML
        </div>
        <div class="endpoint">
            <code>GET /api/themes</code> - 获取主题列表
        </div>
        <div class="endpoint">
            <code>GET /api/themes/{name}</code> - 获取主题详情
        </div>
        <div class="endpoint">
            <code>POST /api/images/upload</code> - 上传并处理图片
        </div>
        <div class="endpoint">
            <code>GET /health</code> - 健康检查
        </div>

        <p><a href="/api/themes">查看可用主题</a></p>
    </body>
    </html>
    """)


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "themes_dir": str(THEMES_DIR)}
