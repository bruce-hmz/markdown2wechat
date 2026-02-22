# Markdown 示例文章

这是一篇示例文章，用于测试 Markdown 转微信公众号工具的各项功能。

## 文本格式

**粗体文本** 和 *斜体文本* 以及 ***粗斜体文本***。

## 列表

### 无序列表
- 项目 1
- 项目 2
  - 子项目 2.1
  - 子项目 2.2
- 项目 3

### 有序列表
1. 第一步
2. 第二步
3. 第三步

## 引用

> 这是一段引用文本。
>
> Markdown 是一种轻量级标记语言，它允许人们使用易读易写的纯文本格式编写文档。

## 代码块

### Python 代码
```python
def fibonacci(n):
    """计算斐波那契数列"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# 测试
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
```

### JavaScript 代码
```javascript
const hello = (name) => {
    console.log(`Hello, ${name}!`);
};

hello('WeChat');
```

## 链接和图片

这是一个 [链接示例](https://github.com)。

## 表格

| 功能 | 状态 | 说明 |
|------|------|------|
| 实时预览 | ✅ | WebSocket 实现 |
| 多主题 | ✅ | JSON 配置 |
| 代码高亮 | ✅ | Pygments 支持 |

## 分割线

---

## 结语

欢迎使用 Markdown 转微信公众号工具！

如果觉得有用，欢迎分享给更多的朋友。
