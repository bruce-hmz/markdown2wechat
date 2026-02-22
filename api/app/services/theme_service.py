"""主题管理服务"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel


class ThemeStyles(BaseModel):
    """主题样式配置"""
    global_: Dict[str, str] = {}
    heading: Dict[str, Dict[str, str]] = {}
    code: Dict[str, Dict[str, str]] = {}
    blockquote: Dict[str, str] = {}
    list_: Dict[str, str] = {}
    link: Dict[str, str] = {}
    image: Dict[str, str] = {}
    table: Optional[Dict[str, Dict[str, str]]] = {}

    class Config:
        populate_by_name = True  # Pydantic v2 新配置

    def __init__(self, **data):
        # 处理字段映射
        if 'global' in data:
            data['global_'] = data.pop('global')
        if 'list' in data:
            data['list_'] = data.pop('list')
        super().__init__(**data)


class Theme(BaseModel):
    """主题配置"""
    name: str
    version: str = "1.0"
    styles: ThemeStyles


class ThemeService:
    """主题管理服务"""

    def __init__(self, themes_dir: str = None):
        """
        初始化主题服务

        Args:
            themes_dir: 主题目录路径
        """
        if themes_dir is None:
            # 使用相对于当前文件的路径
            # api/app/services/theme_service.py -> api/themes/
            base_dir = Path(__file__).resolve().parent.parent.parent  # api/
            themes_dir = base_dir / "themes"

        self.themes_dir = Path(themes_dir)
        self._cache: Dict[str, Theme] = {}

    def list_themes(self) -> list[str]:
        """
        获取所有可用主题列表

        Returns:
            主题名称列表
        """
        if not self.themes_dir.exists():
            return []

        themes = []
        for theme_file in self.themes_dir.glob("*.json"):
            themes.append(theme_file.stem)

        return sorted(themes)

    def load_theme(self, theme_name: str = "default") -> Theme:
        """
        加载主题配置

        Args:
            theme_name: 主题名称

        Returns:
            主题配置对象

        Raises:
            FileNotFoundError: 主题文件不存在
            ValueError: 主题配置格式错误
        """
        # 检查缓存
        if theme_name in self._cache:
            return self._cache[theme_name]

        # 读取主题文件
        theme_path = self.themes_dir / f"{theme_name}.json"
        if not theme_path.exists():
            raise FileNotFoundError(f"主题文件不存在: {theme_path}")

        with open(theme_path, 'r', encoding='utf-8') as f:
            theme_data = json.load(f)

        # 验证并创建主题对象
        try:
            theme = Theme(**theme_data)
            self._cache[theme_name] = theme
            return theme
        except Exception as e:
            raise ValueError(f"主题配置格式错误: {e}")

    def theme_to_css(self, theme: Theme) -> str:
        """
        将主题配置转换为 CSS

        Args:
            theme: 主题配置对象

        Returns:
            CSS 样式字符串
        """
        css_rules = []

        # 全局样式 - 应用到常见文本元素，避免 background-color 被 premailer 内联到所有元素
        if theme.styles.global_:
            # 确保添加透明的背景色，避免灰色背景
            styles_with_bg = dict(theme.styles.global_)
            styles_with_bg['background-color'] = 'transparent'
            global_css = self._dict_to_css(styles_with_bg)
            # 应用到段落、列表、引用等，但不包括 body
            css_rules.append(f"p, ul, ol, li, div {{ {global_css} }}")

        # 标题样式（确保没有背景色）
        for tag, styles in theme.styles.heading.items():
            styles_with_bg = dict(styles)
            if 'background-color' not in styles_with_bg:
                styles_with_bg['background-color'] = 'transparent'
            css = self._dict_to_css(styles_with_bg)
            css_rules.append(f"{tag} {{ {css} }}")

        # 代码样式
        if theme.styles.code:
            # 代码块样式只应用给 pre 标签
            if 'block' in theme.styles.code:
                styles_with_bg = dict(theme.styles.code['block'])
                if 'background-color' not in styles_with_bg:
                    styles_with_bg['background-color'] = 'transparent'
                css = self._dict_to_css(styles_with_bg)
                css_rules.append(f"pre {{ {css} }}")
            # 行内代码样式应用给 code 标签
            if 'inline' in theme.styles.code:
                styles_with_bg = dict(theme.styles.code['inline'])
                if 'background-color' not in styles_with_bg:
                    styles_with_bg['background-color'] = 'transparent'
                css = self._dict_to_css(styles_with_bg)
                css_rules.append(f"code {{ {css} }}")

        # 引用样式
        if theme.styles.blockquote:
            styles_with_bg = dict(theme.styles.blockquote)
            if 'background-color' not in styles_with_bg:
                styles_with_bg['background-color'] = 'transparent'
            css = self._dict_to_css(styles_with_bg)
            css_rules.append(f"blockquote {{ {css} }}")

        # 列表样式
        if theme.styles.list_:
            styles_with_bg = dict(theme.styles.list_)
            if 'background-color' not in styles_with_bg:
                styles_with_bg['background-color'] = 'transparent'
            css = self._dict_to_css(styles_with_bg)
            css_rules.append(f"ul, ol {{ {css} }}")

        # 链接样式
        if theme.styles.link:
            styles_with_bg = dict(theme.styles.link)
            if 'background-color' not in styles_with_bg:
                styles_with_bg['background-color'] = 'transparent'
            css = self._dict_to_css(styles_with_bg)
            css_rules.append(f"a {{ {css} }}")

        # 图片样式
        if theme.styles.image:
            styles_with_bg = dict(theme.styles.image)
            if 'background-color' not in styles_with_bg:
                styles_with_bg['background-color'] = 'transparent'
            css = self._dict_to_css(styles_with_bg)
            css_rules.append(f"img {{ {css} }}")

        # 表格样式
        if theme.styles.table:
            if 'table' in theme.styles.table:
                styles_with_bg = dict(theme.styles.table['table'])
                if 'background-color' not in styles_with_bg:
                    styles_with_bg['background-color'] = 'transparent'
                css = self._dict_to_css(styles_with_bg)
                css_rules.append(f"table {{ {css} }}")
            if 'th' in theme.styles.table:
                styles_with_bg = dict(theme.styles.table['th'])
                if 'background-color' not in styles_with_bg:
                    styles_with_bg['background-color'] = 'transparent'
                css = self._dict_to_css(styles_with_bg)
                css_rules.append(f"th {{ {css} }}")
            if 'td' in theme.styles.table:
                styles_with_bg = dict(theme.styles.table['td'])
                if 'background-color' not in styles_with_bg:
                    styles_with_bg['background-color'] = 'transparent'
                css = self._dict_to_css(styles_with_bg)
                css_rules.append(f"td {{ {css} }}")

        return "\n".join(css_rules)

    def _dict_to_css(self, styles: Dict[str, str]) -> str:
        """
        将样式字典转换为 CSS 字符串

        Args:
            styles: 样式字典

        Returns:
            CSS 字符串
        """
        return "; ".join(f"{k}: {v}" for k, v in styles.items())

    def clear_cache(self):
        """清除主题缓存"""
        self._cache.clear()
