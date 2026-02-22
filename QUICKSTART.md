# 快速启动指南

## 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

## 2. 启动应用

### 方法一：使用启动脚本（推荐）
```bash
./start.sh
```

### 方法二：手动启动
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 3. 访问应用

打开浏览器访问：http://localhost:8000

## 4. 使用流程

1. 在左侧编辑器中输入 Markdown 内容
2. 右侧实时预览转换效果
3. 选择喜欢的主题样式
4. 点击"复制到剪贴板"
5. 在微信公众号编辑器中粘贴

## 常用操作

- **切换主题**：点击顶部主题下拉框选择
- **实时预览**：输入内容自动预览（300ms 防抖）
- **复制内容**：点击"复制到剪贴板"按钮
- **上传图片**：在编辑器中点击图片按钮上传

## 故障排除

### 依赖安装失败
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 端口被占用
修改启动命令中的端口号：
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### WebSocket 连接失败
检查浏览器控制台错误信息，确保：
1. 应用已正常启动
2. 访问地址正确（http://localhost:8000）
3. 没有防火墙或代理阻止 WebSocket 连接

## 开发模式

启动开发服务器（自动重载）：
```bash
uvicorn app.main:app --reload
```

查看 API 文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 生产部署

建议使用 Gunicorn + Uvicorn：
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```
