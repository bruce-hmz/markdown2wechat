"""CSS 内联转换工具"""

from premailer import transform
from typing import Optional


def apply_inline_styles(html: str, css: str) -> str:
    """
    将 CSS 转换为内联样式（微信公众号必需）

    Args:
        html: HTML 内容
        css: CSS 样式

    Returns:
        内联样式的 HTML
    """
    html_with_style = f"<style>{css}</style>{html}"
    return transform(html_with_style)
