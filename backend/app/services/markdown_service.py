"""Markdown 转换服务"""

import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.toc import TocExtension
from typing import Optional
from bs4 import BeautifulSoup

from app.services.wechat_formatter import format_for_wechat
from app.services.theme_service import Theme, ThemeService
from app.utils.css_inliner import apply_inline_styles
from app.utils.ascii_to_image import is_ascii_box_art, process_code_block as ascii_process_code_block


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

    def _preserve_format_for_wechat(self, text: str, font_size: int = 15) -> str:
        """
        将代码文本转换为微信兼容格式
        每行用 div nowrap 包裹，防止手机端行内换行导致格式错乱
        """
        # 先转义 HTML 特殊字符
        text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        # Tab 转为 4 个空格
        text = text.replace('\t', '    ')
        # 空格转 &nbsp;（保留缩进和对齐）
        text = text.replace(' ', '&nbsp;')
        
        # 按行分割，每行用 div nowrap 包裹
        lines = text.split('\n')
        wrapped_lines = []
        for line in lines:
            wrapped_lines.append(f'<div style="white-space: nowrap; font-size: {font_size}px;">{line}</div>')
        
        return ''.join(wrapped_lines)
    
    def _calculate_font_size(self, text: str) -> int:
        """
        根据代码块最长行计算合适的字体大小
        """
        lines = text.split('\n')
        max_line_len = max(len(line) for line in lines) if lines else 0
        
        # 手机屏幕可用宽度约 343px
        available_width = 343
        char_width_ratio = 0.6
        
        if max_line_len > 0:
            needed_font_size = int(available_width / (max_line_len * char_width_ratio))
            # 限制在 12px - 16px 之间（增大最小值）
            return max(12, min(16, needed_font_size))
        
        return 15  # 默认增大

    def _process_code_block(self, code_text: str) -> str:
        """
        处理单个代码块
        - ASCII 框线图：使用特殊样式（不换行）
        - 普通代码：使用默认样式
        """
        # 先尝试 ASCII 框线图处理
        try:
            result = ascii_process_code_block(code_text)
            if result:
                return result
        except Exception as e:
            print(f"ASCII 处理失败: {e}")
        
        # 普通代码块：使用文本格式
        font_size = self._calculate_font_size(code_text)
        formatted_code = self._preserve_format_for_wechat(code_text, font_size)
        
        code_block_style = (
            "background-color: #f6f8fa; "
            "border: 1px solid #e0e0e0; "
            "padding: 16px; "
            "border-radius: 8px; "
            "margin: 20px 0; "
            "font-family: Consolas, Monaco, 'Courier New', 'Liberation Mono', monospace; "
            f"font-size: {font_size}px; "
            "line-height: 1.6; "
            "color: #24292e;"
        )
        
        return f'<section style="{code_block_style}"><code style="font-family: inherit;">{formatted_code}</code></section>'

    def process_code_blocks(self, html: str) -> str:
        """
        处理代码块，替换为自定义的高亮样式
        """
        # 内联 code 标签样式
        inline_code_style = (
            "background-color: rgba(27,31,35,.05); "
            "padding: 2px 6px; "
            "border-radius: 3px; "
            "font-family: Consolas, Monaco, 'Courier New', monospace; "
            "font-size: 15px; "
            "color: #c7254e;"
        )
        
        soup = BeautifulSoup(html, 'lxml')
        
        # 处理 codehilite 生成的 <div class="highlight"> 代码块
        for div_highlight in soup.find_all('div', class_='highlight'):
            pre = div_highlight.find('pre')
            if pre:
                code_text = pre.get_text()
                processed = self._process_code_block(code_text)
                from bs4 import BeautifulSoup as BS
                new_element = BS(processed, 'lxml')
                if new_element.body:
                    div_highlight.replace_with(new_element.body.next_element)
        
        # 处理独立的 <pre><code> 代码块
        for pre in soup.find_all('pre'):
            code = pre.find('code')
            if code and not pre.find_parent('section'):
                code_text = code.get_text()
                processed = self._process_code_block(code_text)
                from bs4 import BeautifulSoup as BS
                new_element = BS(processed, 'lxml')
                if new_element.body:
                    pre.replace_with(new_element.body.next_element)
        
        # 处理行内代码
        for code in soup.find_all('code'):
            if not code.find_parent('section'):
                code['style'] = inline_code_style
        
        return str(soup)

    def convert_to_wechat_html(
        self,
        markdown_text: str,
        theme: Optional[Theme] = None
    ) -> str:
        """
        将 Markdown 转换为微信公众号可用的 HTML
        """
        # 1. 转换为 HTML
        html = self.convert_to_html(markdown_text)

        # 2. 处理代码块
        html = self.process_code_blocks(html)

        # 3. 格式化为微信格式
        html = format_for_wechat(html)

        # 4. 应用主题样式
        if theme:
            theme_service = ThemeService()
            css = theme_service.theme_to_css(theme)
            html = apply_inline_styles(html, css)

        return html

    def extract_metadata(self, markdown_text: str) -> dict:
        """
        从 Markdown 中提取元数据
        """
        lines = markdown_text.split('\n')
        metadata = {
            'title': None,
            'word_count': len(markdown_text),
            'line_count': len(lines)
        }

        for line in lines:
            if line.startswith('# '):
                metadata['title'] = line[2:].strip()
                break

        return metadata
