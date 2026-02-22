"""图片处理 API 路由"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.services.image_service import ImageService


router = APIRouter(prefix="/api/images", tags=["images"])


class ImageUploadResponse(BaseModel):
    """图片上传响应"""
    success: bool
    base64: Optional[str] = None
    size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    error: Optional[str] = None


@router.post("/upload", response_model=ImageUploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    quality: int = 85
):
    """
    上传并处理图片

    Args:
        file: 上传的图片文件
        quality: 压缩质量（0-100）

    Returns:
        处理结果
    """
    image_service = ImageService()

    # 验证图片
    is_valid, error_msg = image_service.validate_image(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    try:
        # 重置文件指针
        await file.seek(0)

        # 处理图片
        result = await image_service.process_image(file, quality)

        return ImageUploadResponse(
            success=True,
            base64=result['base64'],
            size=result['size'],
            width=result['width'],
            height=result['height']
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图片处理失败: {str(e)}")
