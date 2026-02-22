"""
微信公众号 Markdown 工具 - FastAPI 应用入口
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

# 静态文件目录
BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
PROJECT_ROOT = BASE_DIR.parent  # wechat-markdown-tool/
STATIC_DIR = PROJECT_ROOT / "frontend" / "static"
TEMPLATES_DIR = PROJECT_ROOT / "frontend" / "templates"
THEMES_DIR = BASE_DIR / "themes"

# 确保目录存在
STATIC_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
THEMES_DIR.mkdir(parents=True, exist_ok=True)

# 挂载静态文件
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
    if not index_file.exists():
        return {"error": "index.html not found"}
    return FileResponse(str(index_file))


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
