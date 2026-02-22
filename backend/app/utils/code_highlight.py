"""代码语法高亮工具"""

from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound
from typing import Optional


def highlight_code(code: str, language: Optional[str] = None) -> str:
    """
    高亮代码并返回内联样式的 HTML

    Args:
        code: 代码内容
        language: 编程语言（可选）

    Returns:
        高亮后的 HTML
    """
    try:
        if language:
            lexer = get_lexer_by_name(language, stripall=True)
        else:
            lexer = guess_lexer(code)
    except ClassNotFound:
        # 如果无法识别语言，使用纯文本
        lexer = get_lexer_by_name('text', stripall=True)

    # noclasses=True 确保使用内联样式而不是 CSS 类
    # nowrap=True 不添加额外的包装标签
    formatter = HtmlFormatter(noclasses=True, nowrap=True)
    return highlight(code, lexer, formatter)


def get_code_block_with_style(code: str, language: Optional[str] = None) -> str:
    """
    获取带样式容器的代码块

    Args:
        code: 代码内容
        language: 编程语言（可选）

    Returns:
        带样式容器的代码块 HTML
    """
    highlighted = highlight_code(code, language)
    # 添加代码块容器样式（不使用背景色）
    return f'<section style="border: 1px solid #e0e0e0; padding: 15px; border-radius: 5px; overflow-x: auto; margin: 20px 0; font-family: Consolas, Monaco, monospace; font-size: 14px; line-height: 1.5;">{highlighted}</section>'
