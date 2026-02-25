"""ASCII 框线图处理工具"""

import re


def has_chinese(text: str) -> bool:
    """检测文本是否包含中文"""
    return any('\u4e00' <= c <= '\u9fff' for c in text)


def is_ascii_box_art(text: str) -> bool:
    """检测是否为 ASCII 框线图"""
    # 排除 Markdown 表格
    lines = [l.strip() for l in text.strip().split('\n') if l.strip()]
    if len(lines) >= 2:
        if re.match(r'^[\|\s\-:]+$', lines[1]) and all('|' in l for l in lines):
            return False
    
    # 必须有角落字符
    corner_chars = set('┌┐└┘╭╮╯╰╔╗╚╝')
    if sum(1 for c in text if c in corner_chars) < 4:
        return False
    
    # 必须有水平线和垂直线
    return ('─' in text or '═' in text) and ('│' in text or '║' in text)


def get_ascii_block_style(has_chinese: bool) -> str:
    """获取 ASCII 框线图的样式（强制不换行）"""
    font_size = 12 if has_chinese else 14
    
    return (
        f"background-color: #f6f8fa; "
        f"border: 1px solid #e0e0e0; "
        "padding: 16px; "
        "border-radius: 8px; "
        "margin: 20px 0; "
        # 强制使用等宽字体
        "font-family: 'Menlo', 'Monaco', 'Consolas', 'Courier New', monospace; "
        f"font-size: {font_size}px; "
        "line-height: 1.5; "
        "color: #24292e; "
        # 关键：强制不换行，允许横向滚动
        "white-space: nowrap; "
        "overflow-x: auto; "
        "word-wrap: normal;"
    )


def format_ascii_text(text: str) -> str:
    """格式化 ASCII 文本为 HTML（逐行转义）"""
    # 转义 HTML 特殊字符
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    # Tab 转为 4 个空格
    text = text.replace('\t', '    ')
    # 空格转 &nbsp;
    text = text.replace(' ', '&nbsp;')
    
    # 按行分割，每行单独 div
    lines = text.split('\n')
    wrapped_lines = [f'<div style="white-space: nowrap; font-size: inherit;">{line}</div>' for line in lines]
    
    return ''.join(wrapped_lines)


def process_code_block(code_text: str) -> str:
    """
    处理代码块
    - ASCII 框线图：使用特殊样式（不换行）
    - 普通代码：使用默认样式
    """
    if is_ascii_box_art(code_text):
        has_cn = has_chinese(code_text)
        style = get_ascii_block_style(has_cn)
        formatted = format_ascii_text(code_text)
        return f'<section style="{style}"><code style="font-family: inherit;">{formatted}</code></section>'
    
    return None
