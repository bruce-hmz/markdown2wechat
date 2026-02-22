/**
 * Markdown 转微信公众号格式工具 - 前端核心逻辑
 */

class MarkdownTool {
    constructor() {
        this.websocket = null;
        this.editor = null;
        this.debounceTimer = null;
        this.currentTheme = 'default';
        this.isConnected = false;

        this.init();
    }

    /**
     * 初始化应用
     */
    async init() {
        // 初始化编辑器
        this.initEditor();

        // 连接 WebSocket
        this.connectWebSocket();

        // 绑定事件
        this.bindEvents();

        // 加载主题列表
        await this.loadThemes();

        // 设置默认内容
        this.setDefaultContent();
    }

    /**
     * 初始化 Markdown 编辑器
     */
    initEditor() {
        this.editor = new EasyMDE({
            element: document.getElementById('editor'),
            autofocus: true,
            spellChecker: false,
            placeholder: '在这里输入 Markdown 内容...',
            toolbar: [
                'bold',
                'italic',
                'heading',
                '|',
                'quote',
                'code',
                'unordered-list',
                'ordered-list',
                '|',
                'link',
                'image',
                '|',
                'preview',
                'side-by-side',
                'fullscreen',
                '|',
                'guide'
            ],
            status: ['autosave', 'lines', 'words'],
            previewRender: (plainText) => {
                // 使用自定义预览
                return '<div class="placeholder">右侧查看实时预览</div>';
            }
        });

        // 监听编辑器变化
        this.editor.codemirror.on('change', () => {
            this.onEditorChange();
        });
    }

    /**
     * 连接 WebSocket
     */
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/convert`;

        this.websocket = new WebSocket(wsUrl);

        this.websocket.onopen = () => {
            console.log('WebSocket 连接成功');
            this.isConnected = true;

            // 如果已有内容，立即转换
            const content = this.editor.value();
            if (content.trim()) {
                this.convertMarkdown(content);
            }
        };

        this.websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };

        this.websocket.onerror = (error) => {
            console.error('WebSocket 错误:', error);
            this.isConnected = false;
        };

        this.websocket.onclose = () => {
            console.log('WebSocket 连接关闭');
            this.isConnected = false;

            // 3秒后重连
            setTimeout(() => {
                this.connectWebSocket();
            }, 3000);
        };
    }

    /**
     * 处理 WebSocket 消息
     */
    handleWebSocketMessage(data) {
        if (data.type === 'success') {
            // 更新预览
            this.updatePreview(data.html);

            // 更新字数统计
            if (data.metadata) {
                document.getElementById('word-count').textContent =
                    `${data.metadata.word_count} 字`;
            }
        } else if (data.type === 'error') {
            console.error('转换错误:', data.message);
            this.showError(data.message);
        }
    }

    /**
     * 绑定事件
     */
    bindEvents() {
        // 主题切换
        document.getElementById('theme-select').addEventListener('change', (e) => {
            this.currentTheme = e.target.value;
            this.convertMarkdown(this.editor.value());
        });

        // 复制按钮
        document.getElementById('copy-btn').addEventListener('click', () => {
            this.copyToClipboard();
        });

        // 回到顶部按钮
        this.initBackToTop();
    }

    /**
     * 初始化回到顶部按钮
     */
    initBackToTop() {
        const preview = document.getElementById('preview');
        const backToTopBtn = document.getElementById('back-to-top');

        // 监听预览区滚动
        preview.addEventListener('scroll', () => {
            if (preview.scrollTop > 200) {
                backToTopBtn.classList.add('visible');
            } else {
                backToTopBtn.classList.remove('visible');
            }
        });

        // 点击回到顶部
        backToTopBtn.addEventListener('click', () => {
            preview.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    /**
     * 加载主题列表
     */
    async loadThemes() {
        try {
            const response = await fetch('/api/themes');
            const data = await response.json();

            const select = document.getElementById('theme-select');
            select.innerHTML = '';

            data.themes.forEach(theme => {
                const option = document.createElement('option');
                option.value = theme.file.replace('.json', '');
                option.textContent = theme.name;
                select.appendChild(option);
            });

            // 设置当前主题
            select.value = this.currentTheme;

        } catch (error) {
            console.error('加载主题失败:', error);
        }
    }

    /**
     * 编辑器变化处理（带防抖）
     */
    onEditorChange() {
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
            const content = this.editor.value();
            this.convertMarkdown(content);
        }, 300);
    }

    /**
     * 转换 Markdown
     */
    convertMarkdown(markdown) {
        if (!markdown.trim()) {
            document.getElementById('preview').innerHTML =
                '<p class="placeholder">在左侧输入 Markdown 内容，这里将实时显示预览效果...</p>';
            return;
        }

        if (this.isConnected && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify({
                markdown: markdown,
                theme: this.currentTheme
            }));
        } else {
            // WebSocket 未连接时使用 HTTP API
            this.convertViaHttp(markdown);
        }
    }

    /**
     * 通过 HTTP API 转换
     */
    async convertViaHttp(markdown) {
        try {
            const response = await fetch('/api/convert', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    markdown: markdown,
                    theme: this.currentTheme
                })
            });

            const data = await response.json();
            this.updatePreview(data.html);

            document.getElementById('word-count').textContent =
                `${data.metadata.word_count} 字`;

        } catch (error) {
            console.error('转换失败:', error);
            this.showError('转换失败，请重试');
        }
    }

    /**
     * 更新预览内容
     */
    updatePreview(html) {
        const preview = document.getElementById('preview');
        preview.innerHTML = html;
    }

    /**
     * 复制到剪贴板
     */
    async copyToClipboard() {
        const preview = document.getElementById('preview');
        const html = preview.innerHTML;

        try {
            // 方法1：尝试使用现代 Clipboard API（支持富文本）
            if (navigator.clipboard && navigator.clipboard.write) {
                const blob = new Blob([html], { type: 'text/html' });
                const clipboardItem = new ClipboardItem({ 'text/html': blob });
                await navigator.clipboard.write([clipboardItem]);

                this.showSuccess('已复制到剪贴板，可直接粘贴到微信公众号编辑器');
                return;
            }

            // 方法2：降级方案（旧版浏览器）
            // 创建临时元素
            const temp = document.createElement('div');
            temp.innerHTML = html;
            temp.style.position = 'absolute';
            temp.style.left = '-9999px';
            temp.style.backgroundColor = 'white'; // 确保背景是白色
            document.body.appendChild(temp);

            // 选择内容
            const range = document.createRange();
            range.selectNodeContents(temp);
            const selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);

            // 复制
            document.execCommand('copy');

            // 清理
            document.body.removeChild(temp);
            selection.removeAllRanges();

            // 显示成功提示
            this.showSuccess('已复制到剪贴板，可直接粘贴到微信公众号编辑器');

        } catch (error) {
            console.error('复制失败:', error);
            this.showError('复制失败，请手动选择内容复制');
        }
    }

    /**
     * 显示成功消息
     */
    showSuccess(message) {
        const msg = document.createElement('div');
        msg.className = 'success-message';
        msg.textContent = message;
        document.body.appendChild(msg);

        setTimeout(() => {
            msg.remove();
        }, 3000);
    }

    /**
     * 显示错误消息
     */
    showError(message) {
        const msg = document.createElement('div');
        msg.className = 'success-message';
        msg.style.background = '#ef4444';
        msg.textContent = message;
        document.body.appendChild(msg);

        setTimeout(() => {
            msg.remove();
        }, 3000);
    }

    /**
     * 设置默认内容
     */
    setDefaultContent() {
        const defaultContent = `# 欢迎使用 Markdown 转微信公众号工具

这是一个简单易用的工具，可以将 Markdown 格式的文章转换为可以直接粘贴到微信公众号编辑器的富文本格式。

## 主要功能

- ✅ **实时预览**：边写边看，所见即所得
- ✅ **多种主题**：支持多种排版风格
- ✅ **代码高亮**：支持数百种编程语言
- ✅ **图片处理**：自动优化图片尺寸和质量

## 使用方法

1. 在左侧编辑器中输入 Markdown 内容
2. 右侧将实时显示转换效果
3. 点击"复制到剪贴板"按钮
4. 在微信公众号编辑器中粘贴即可

## 代码示例

\`\`\`python
def hello_world():
    print("Hello, WeChat!")
\`\`\`

## 引用示例

> Markdown 是一种轻量级标记语言，它允许人们使用易读易写的纯文本格式编写文档。

---

开始你的创作吧！
`;

        this.editor.value(defaultContent);
    }
}

// 初始化应用 - 等待所有脚本加载完成
window.onload = function() {
    // 确保 EasyMDE 已加载
    if (typeof EasyMDE !== 'undefined') {
        new MarkdownTool();
    } else {
        // 如果 EasyMDE 还没加载，等待一小段时间重试
        const checkInterval = setInterval(() => {
            if (typeof EasyMDE !== 'undefined') {
                clearInterval(checkInterval);
                new MarkdownTool();
            }
        }, 100);

        // 5秒后超时提示
        setTimeout(() => {
            clearInterval(checkInterval);
            if (typeof EasyMDE === 'undefined') {
                console.error('EasyMDE 加载失败，请刷新页面重试');
            }
        }, 5000);
    }
};
