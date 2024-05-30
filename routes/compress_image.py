from fastapi import  HTTPException, status
import io
from PIL import Image

async def compress_image(image_content: bytes, max_size_mb: int = 2, max_dimensions: tuple = (1024, 1024)) -> bytes:
    with Image.open(io.BytesIO(image_content)) as img:
        img.thumbnail(max_dimensions)  # Ajusta el tamaño máximo
        output = io.BytesIO()
        quality = 95
        img.save(output, format="PNG", quality=quality)
        
        while output.tell() > max_size_mb * 1024 * 1024 and quality > 10:
            output = io.BytesIO()
            quality -= 5
            img.save(output, format="PNG", quality=quality)
        
        if output.tell() > max_size_mb * 1024 * 1024:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Intenta subir una imagen de menor tamaño.")
        
        return output.getvalue()