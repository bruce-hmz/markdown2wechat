"""
微信公众号 Markdown 工具 - FastAPI 应用入口
"""

import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
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

# 静态文件目录 - 适配 Vercel 和本地开发
def get_base_dirs():
    """获取基础目录路径"""
    # 当前文件位置: backend/app/main.py
    BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
    PROJECT_ROOT = BASE_DIR.parent  # 项目根目录

    # 检查是否在 Vercel 环境中运行
    if os.environ.get("VERCEL"):
        # Vercel 环境：使用 VERCEL_ROOT 或当前工作目录
        vercel_root = os.environ.get("VERCEL_ROOT", os.getcwd())
        PROJECT_ROOT = Path(vercel_root)
        BASE_DIR = PROJECT_ROOT / "backend"

    STATIC_DIR = PROJECT_ROOT / "frontend" / "static"
    TEMPLATES_DIR = PROJECT_ROOT / "frontend" / "templates"
    THEMES_DIR = BASE_DIR / "themes"

    return STATIC_DIR, TEMPLATES_DIR, THEMES_DIR, PROJECT_ROOT, BASE_DIR

STATIC_DIR, TEMPLATES_DIR, THEMES_DIR, PROJECT_ROOT, BASE_DIR = get_base_dirs()

# 确保目录存在（仅在本地开发时）
if not os.environ.get("VERCEL"):
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    THEMES_DIR.mkdir(parents=True, exist_ok=True)

# 挂载静态文件（仅在目录存在时）
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# 导入路由
from app.routers import markdown, themes, images

# 注册路由
app.include_router(markdown.router)
app.include_router(themes.router)
app.include_router(images.router)


@app.get("/")
async def index():
    """主页面"""
    index_file = TEMPLATES_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))

    # 如果文件不存在，返回简单的 HTML
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head><title>Markdown2WeChat</title></head>
    <body>
        <h1>Loading...</h1>
        <p>If you see this, the frontend is not deployed correctly.</p>
    </body>
    </html>
    """)


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "static_dir": str(STATIC_DIR), "themes_dir": str(THEMES_DIR)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
