"""Markdown 转换服务"""

import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.toc import TocExtension
from typing import Optional
import re

from app.services.wechat_formatter import format_for_wechat
from app.services.theme_service import Theme, ThemeService
from app.utils.css_inliner import apply_inline_styles
from app.utils.code_highlight import get_code_block_with_style


class MarkdownService:
    """Markdown 转换服务"""

    def __init__(self):
        """初始化 Markdown 服务"""
        self.md = markdown.Markdown(
            extensions=[
                'fenced_code',
                'codehilite',
                'tables',
                'toc',
                'nl2br',
                'sane_lists'
            ],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight',
                    'linenums': False,
                    'guess_lang': True
                }
            }
        )

    def convert_to_html(self, text: str) -> str:
        """
        将 Markdown 转换为 HTML

        Args:
            text: Markdown 文本

        Returns:
            HTML 内容
        """
        self.md.reset()
        return self.md.convert(text)

    def process_code_blocks(self, html: str) -> str:
        """
        处理代码块，替换为自定义的高亮样式

        Args:
            html: HTML 内容

        Returns:
            处理后的 HTML
        """
        # 匹配 <pre><code class="language-xxx"> 的代码块
        pattern = r'<pre><code(?:\s+class="language-(\w+)")?>(.*?)</code></pre>'

        def replace_code_block(match):
            language = match.group(1)
            code = match.group(2)
            # 解码 HTML 实体
            code = code.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
            return get_code_block_with_style(code, language)

        return re.sub(pattern, replace_code_block, html, flags=re.DOTALL)

    def convert_to_wechat_html(
        self,
        markdown_text: str,
        theme: Optional[Theme] = None
    ) -> str:
        """
        将 Markdown 转换为微信公众号可用的 HTML

        Args:
            markdown_text: Markdown 文本
            theme: 主题配置（可选）

        Returns:
            微信公众号格式的 HTML
        """
        # 1. 转换为 HTML
        html = self.convert_to_html(markdown_text)

        # 2. 处理代码块
        html = self.process_code_blocks(html)

        # 3. 格式化为微信格式（先清理和优化）
        html = format_for_wechat(html)

        # 4. 应用主题样式（最后应用，不会被覆盖）
        if theme:
            theme_service = ThemeService()
            css = theme_service.theme_to_css(theme)
            html = apply_inline_styles(html, css)

        return html

    def extract_metadata(self, markdown_text: str) -> dict:
        """
        从 Markdown 中提取元数据

        Args:
            markdown_text: Markdown 文本

        Returns:
            元数据字典
        """
        lines = markdown_text.split('\n')
        metadata = {
            'title': None,
            'word_count': len(markdown_text),
            'line_count': len(lines)
        }

        # 尝试提取第一个标题作为标题
        for line in lines:
            if line.startswith('# '):
                metadata['title'] = line[2:].strip()
                break

        return metadata
