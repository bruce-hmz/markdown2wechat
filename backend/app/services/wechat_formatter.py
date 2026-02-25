"""微信格式化核心服务"""

from bs4 import BeautifulSoup
from typing import Set


# 微信公众号支持的 HTML 标签
SUPPORTED_TAGS: Set[str] = {
'p', 'br', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
'strong', 'em', 'b', 'i', 'u', 's', 'blockquote',
    'ul', 'ol', 'li', 'img', 'a', 'section',
    # 代码块标签
    'pre', 'code',
# 表格标签
'table', 'thead', 'tbody', 'tr', 'th', 'td', 'caption'
}

# 需要移除的标签属性（保留 style）
REMOVE_ATTRS: Set[str] = {'class', 'id', 'data-*'}


def sanitize_html(html: str) -> str:
    """
    清理不支持的 HTML 标签和属性

    Args:
        html: 原始 HTML

    Returns:
        清理后的 HTML
    """
    soup = BeautifulSoup(html, 'lxml')

    # 处理所有标签
    for tag in soup.find_all(True):
        # 移除不支持的标签（解包保留内容）
        if tag.name not in SUPPORTED_TAGS:
            tag.unwrap()
        else:
            # 移除不需要的属性，只保留 style 和 href/src
            attrs_to_remove = []
            for attr in tag.attrs:
                if attr not in ['style', 'href', 'src', 'alt']:
                    attrs_to_remove.append(attr)
            for attr in attrs_to_remove:
                del tag[attr]

    # 移除 body 和 html 标签（如果存在）
    if soup.body:
        return ''.join(str(child) for child in soup.body.children)

    return str(soup)


def optimize_for_mobile(html: str) -> str:
    """
    优化移动端显示

    Args:
        html: HTML 内容

    Returns:
        优化后的 HTML
    """
    soup = BeautifulSoup(html, 'lxml')

    # 优化图片：添加宽度限制
    for img in soup.find_all('img'):
        style = img.get('style', '')
        if 'max-width' not in style:
            img['style'] = f'{style}; max-width: 100%; height: auto; display: block; margin: 20px auto;'

    # 优化段落：添加合适的行高
    for p in soup.find_all('p'):
        style = p.get('style', '')
        if 'line-height' not in style:
            p['style'] = f'{style}; line-height: 1.75; margin: 15px 0;'

    # 优化标题：添加间距
    for i in range(1, 7):
        for h in soup.find_all(f'h{i}'):
            style = h.get('style', '')
            if 'margin' not in style:
                h['style'] = f'{style}; margin: 25px 0 15px;'

    # 优化表格：添加样式以适配移动端
    for table in soup.find_all('table'):
        style = table.get('style', '')
        if 'width' not in style:
            table['style'] = f'{style}; width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 14px; overflow-x: auto;'

    # 优化表格单元格（只在没有样式时添加基础样式）
    for th in soup.find_all('th'):
        style = th.get('style', '')
        if not style or 'padding' not in style:
            th['style'] = f'{style}; padding: 10px; border: 1px solid #ddd; font-weight: bold; text-align: left;'

    for td in soup.find_all('td'):
        style = td.get('style', '')
        if not style or 'padding' not in style:
            td['style'] = f'{style}; padding: 10px; border: 1px solid #ddd;'

    # 优化代码块容器 section（跳过已有样式的代码块）
    for section in soup.find_all('section'):
        style = section.get('style', '')
        # 只处理没有样式的 section，避免覆盖代码块样式
        if not style:
            section['style'] = 'margin: 15px 0;'

    # 优化 pre 标签（如果还没有样式）
    for pre in soup.find_all('pre'):
        style = pre.get('style', '')
        if 'white-space' not in style:
            pre['style'] = f'{style}; white-space: pre-wrap; word-wrap: break-word; font-family: Consolas, Monaco, monospace;'

    return str(soup)


def format_for_wechat(html: str) -> str:
    """
    完整的微信格式化流程

    Args:
        html: 原始 HTML

    Returns:
        微信公众号可用的 HTML
    """
    # 1. 清理不支持的标签
    html = sanitize_html(html)

    # 2. 优化移动端显示
    html = optimize_for_mobile(html)

    return html
