"""主题管理 API 路由"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict

from app.services.theme_service import ThemeService, Theme


router = APIRouter(prefix="/api/themes", tags=["themes"])


class ThemeInfo(BaseModel):
    """主题信息"""
    name: str
    version: str
    file: str


class ThemeListResponse(BaseModel):
    """主题列表响应"""
    themes: List[ThemeInfo]
    count: int


class ThemeDetailResponse(BaseModel):
    """主题详情响应"""
    name: str
    version: str
    css: str


@router.get("", response_model=ThemeListResponse)
async def list_themes():
    """
    获取所有可用主题列表

    Returns:
        主题列表
    """
    theme_service = ThemeService()
    theme_names = theme_service.list_themes()

    themes = []
    for name in theme_names:
        try:
            theme = theme_service.load_theme(name)
            themes.append(ThemeInfo(
                name=theme.name,
                version=theme.version,
                file=f"{name}.json"
            ))
        except Exception:
            # 跳过无效的主题文件
            continue

    return ThemeListResponse(
        themes=themes,
        count=len(themes)
    )


@router.get("/{theme_name}", response_model=ThemeDetailResponse)
async def get_theme(theme_name: str):
    """
    获取指定主题的详细信息

    Args:
        theme_name: 主题名称

    Returns:
        主题详情
    """
    theme_service = ThemeService()

    try:
        theme = theme_service.load_theme(theme_name)
        css = theme_service.theme_to_css(theme)

        return ThemeDetailResponse(
            name=theme.name,
            version=theme.version,
            css=css
        )

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"主题不存在: {theme_name}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"加载主题失败: {str(e)}")
