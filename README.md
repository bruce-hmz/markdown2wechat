# Markdown 转微信公众号格式工具

一个简洁高效的本地 Web 应用，将 Markdown 文章转换为可以直接粘贴到微信公众号编辑器的富文本格式。

## 功能特性

- ✅ **实时预览** - WebSocket 实现毫秒级响应，边写边看
- ✅ **多种主题** - 3 种预设主题（默认/优雅/科技），JSON 配置易于扩展
- ✅ **代码高亮** - 支持 500+ 种编程语言的语法高亮
- ✅ **图片处理** - 自动压缩、Base64 转换、移动端尺寸优化
- ✅ **一键复制** - 直接复制为富文本，粘贴即可使用
- ✅ **移动端优化** - 针对微信公众号移动端显示优化

## 技术栈

**后端：**
- FastAPI（异步 Web 框架）
- Python-Markdown（Markdown 解析）
- Pygments（代码语法高亮）
- Premailer（CSS 内联转换）
- Pillow（图片处理）

**前端：**
- EasyMDE（Markdown 编辑器）
- 原生 JavaScript + WebSocket
- 简洁的单页应用

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 启动应用

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 访问应用

打开浏览器访问：http://localhost:8000

### 4. 使用工具

1. 在左侧编辑器中输入 Markdown 内容
2. 右侧将实时显示转换效果
3. 选择喜欢的主题样式
4. 点击"复制到剪贴板"按钮
5. 在微信公众号编辑器中粘贴即可

## 项目结构

```
wechat-markdown-tool/
├── backend/
│   ├── app/
│   │   ├── main.py                          # FastAPI 应用入口
│   │   ├── routers/                         # API 路由
│   │   │   ├── markdown.py                  # Markdown 转换 API
│   │   │   ├── themes.py                    # 主题管理 API
│   │   │   └── images.py                    # 图片处理 API
│   │   ├── services/                        # 核心服务
│   │   │   ├── markdown_service.py          # Markdown 转换
│   │   │   ├── theme_service.py             # 主题管理
│   │   │   ├── image_service.py             # 图片处理
│   │   │   └── wechat_formatter.py          # 微信格式化
│   │   └── utils/                           # 工具函数
│   │       ├── css_inliner.py               # CSS 内联工具
│   │       └── code_highlight.py            # 代码高亮
│   ├── themes/                              # 主题配置
│   │   ├── default.json                     # 默认主题
│   │   ├── elegant.json                     # 优雅主题
│   │   └── tech.json                        # 科技主题
│   └── requirements.txt                     # Python 依赖
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── main.css                     # 样式文件
│   │   └── js/
│   │       └── app.js                       # 前端核心逻辑
│   └── templates/
│       └── index.html                       # 主页面
└── README.md
```

## API 文档

### 1. Markdown 转换 API

**POST /api/convert**
- 描述：同步转换 Markdown 为微信 HTML
- 请求体：
  ```json
  {
    "markdown": "# 标题\n内容",
    "theme": "default"
  }
  ```
- 响应：
  ```json
  {
    "html": "<h1>标题</h1><p>内容</p>",
    "metadata": {
      "title": "标题",
      "word_count": 5,
      "line_count": 2
    }
  }
  ```

**WebSocket /ws/convert**
- 描述：实时转换（边写边看）
- 消息格式：
  ```json
  // 发送
  {
    "markdown": "# 标题",
    "theme": "default"
  }
  // 接收
  {
    "type": "success",
    "html": "<h1>标题</h1>",
    "metadata": {...}
  }
  ```

### 2. 主题管理 API

**GET /api/themes**
- 描述：获取所有可用主题列表
- 响应：
  ```json
  {
    "themes": [
      {"name": "默认主题", "version": "1.0", "file": "default.json"}
    ],
    "count": 3
  }
  ```

**GET /api/themes/{theme_name}**
- 描述：获取指定主题详情
- 响应：
  ```json
  {
    "name": "默认主题",
    "version": "1.0",
    "css": "body { font-size: 16px; }"
  }
  ```

### 3. 图片处理 API

**POST /api/images/upload**
- 描述：上传并处理图片
- 请求：multipart/form-data
- 参数：file（图片文件）、quality（压缩质量，默认 85）
- 响应：
  ```json
  {
    "success": true,
    "base64": "data:image/jpeg;base64,...",
    "size": 45000,
    "width": 750,
    "height": 500
  }
  ```

## 自定义主题

创建新的主题配置文件（如 `my-theme.json`）：

```json
{
  "name": "我的主题",
  "version": "1.0",
  "styles": {
    "global": {
      "font-size": "16px",
      "line-height": "1.75",
      "color": "#333333"
    },
    "heading": {
      "h1": {
        "font-size": "24px",
        "font-weight": "bold",
        "color": "#000000"
      }
    },
    "code": {
      "block": {
        "background": "#2d2d2d",
        "color": "#f8f8f2",
        "padding": "15px"
      }
    }
  }
}
```

将文件保存到 `backend/themes/` 目录，刷新页面即可看到新主题。

## 核心技术要点

1. **内联样式转换** - 使用 `premailer` 库自动转换 CSS 为内联样式（微信公众号必需）
2. **WebSocket 实时通信** - 实现毫秒级响应的实时预览
3. **代码高亮** - 使用 `Pygments` 支持 500+ 种编程语言
4. **移动端优化** - 字体最小 16px、行高 1.75、图片最大宽度 750px
5. **HTML 清理** - 使用 `BeautifulSoup` 移除不支持的标签
6. **图片处理** - Pillow 压缩 + Base64 转换 + 尺寸优化

## 常见问题

### Q: 为什么需要转换为内联样式？
A: 微信公众号编辑器不支持外部 CSS 和 style 标签，所有样式必须内联到 HTML 标签上。

### Q: 支持哪些 Markdown 语法？
A: 支持标准 Markdown 语法，包括标题、段落、列表、代码块、引用、链接、图片、表格等。

### Q: 图片为什么需要转 Base64？
A: 微信公众号对网络图片有限制，Base64 可以确保图片正常显示。建议图片小于 50KB。

### Q: 可以离线使用吗？
A: 可以，所有功能都是本地运行的，只需要首次安装依赖时联网。

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v1.0.0 (2026-02-13)
- ✨ 初始版本发布
- ✨ 支持 3 种预设主题
- ✨ WebSocket 实时预览
- ✨ 图片自动处理
- ✨ 代码语法高亮
