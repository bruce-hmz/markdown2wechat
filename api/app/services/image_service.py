"""图片处理服务"""

from PIL import Image
import io
import base64
from typing import Optional, Tuple
from fastapi import UploadFile


class ImageService:
    """图片处理服务"""

    def __init__(self, max_width: int = 750, max_size_kb: int = 50):
        """
        初始化图片服务

        Args:
            max_width: 最大宽度（像素）
            max_size_kb: Base64 转换的最大文件大小（KB）
        """
        self.max_width = max_width
        self.max_size_kb = max_size_kb

    async def process_image(
        self,
        image_file: UploadFile,
        quality: int = 85
    ) -> dict:
        """
        处理并优化图片

        Args:
            image_file: 上传的图片文件
            quality: JPEG 压缩质量（0-100）

        Returns:
            包含处理结果的字典：
            - base64: Base64 编码的图片（如果小于阈值）
            - size: 文件大小（字节）
            - width: 图片宽度
            - height: 图片高度
        """
        # 读取图片
        image_bytes = await image_file.read()
        img = Image.open(io.BytesIO(image_bytes))

        # 转换为 RGB（如果需要）
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background

        original_size = (img.width, img.height)

        # 调整尺寸（保持宽高比）
        if img.width > self.max_width:
            ratio = self.max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((self.max_width, new_height), Image.Resampling.LANCZOS)

        # 压缩图片
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
        size = len(buffer.getvalue())

        # 如果还是太大，降低质量
        while size > self.max_size_kb * 1024 and quality > 20:
            quality -= 10
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=quality, optimize=True)
            size = len(buffer.getvalue())

        # 转换为 Base64
        base64_str = base64.b64encode(buffer.getvalue()).decode()

        return {
            "base64": f"data:image/jpeg;base64,{base64_str}",
            "size": size,
            "width": img.width,
            "height": img.height,
            "original_width": original_size[0],
            "original_height": original_size[1]
        }

    def validate_image(self, image_file: UploadFile) -> Tuple[bool, Optional[str]]:
        """
        验证图片文件

        Args:
            image_file: 上传的图片文件

        Returns:
            (是否有效, 错误消息)
        """
        # 检查文件类型
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if image_file.content_type not in allowed_types:
            return False, f"不支持的图片类型: {image_file.content_type}"

        # 检查文件大小（最大 10MB）
        if image_file.size and image_file.size > 10 * 1024 * 1024:
            return False, "图片文件过大（最大 10MB）"

        return True, None
