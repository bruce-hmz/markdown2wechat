"""Markdown 转换 API 路由"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from typing import Optional

from api.app.services.markdown_service import MarkdownService
from api.app.services.theme_service import ThemeService


router = APIRouter(prefix="/api", tags=["markdown"])


class ConvertRequest(BaseModel):
    """转换请求"""
    markdown: str
    theme: Optional[str] = "default"


class ConvertResponse(BaseModel):
    """转换响应"""
    html: str
    metadata: dict


@router.post("/convert", response_model=ConvertResponse)
async def convert_markdown(request: ConvertRequest):
    """
    同步转换 Markdown 为微信 HTML

    Args:
        request: 转换请求

    Returns:
        转换结果
    """
    try:
        # 初始化服务
        md_service = MarkdownService()
        theme_service = ThemeService()

        # 加载主题
        theme = theme_service.load_theme(request.theme)

        # 转换
        html = md_service.convert_to_wechat_html(request.markdown, theme)
        metadata = md_service.extract_metadata(request.markdown)

        return ConvertResponse(html=html, metadata=metadata)

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"主题不存在: {request.theme}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"转换失败: {str(e)}")


@router.websocket("/ws/convert")
async def websocket_convert(websocket: WebSocket):
    """
    WebSocket 实时转换（实时预览核心）

    通过 WebSocket 连接实现边写边看的实时预览功能
    """
    await websocket.accept()

    # 初始化服务
    md_service = MarkdownService()
    theme_service = ThemeService()

    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_json()

            markdown_text = data.get('markdown', '')
            theme_name = data.get('theme', 'default')

            try:
                # 加载主题
                theme = theme_service.load_theme(theme_name)

                # 实时转换
                html = md_service.convert_to_wechat_html(markdown_text, theme)
                metadata = md_service.extract_metadata(markdown_text)

                # 发送结果
                await websocket.send_json({
                    "type": "success",
                    "html": html,
                    "metadata": metadata
                })

            except FileNotFoundError:
                await websocket.send_json({
                    "type": "error",
                    "message": f"主题不存在: {theme_name}"
                })
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "message": f"转换失败: {str(e)}"
                })

    except WebSocketDisconnect:
        # 客户端断开连接
        pass
    except Exception as e:
        # 其他错误
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"服务器错误: {str(e)}"
            })
        except:
            pass
