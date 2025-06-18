import os
import shutil
import uuid
from fastapi import HTTPException, UploadFile





import aiofiles

async def save_upload_file(upload_file: UploadFile, upload_dir: str = "static") -> str:
    if not upload_file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file is not an image")

    ext = os.path.splitext(upload_file.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]:
        ext = ".png"

    unique_filename = f"{uuid.uuid4()}{ext}"

    os.makedirs(upload_dir, exist_ok=True)
    abs_path = os.path.join(upload_dir, unique_filename)

    try:
        async with aiofiles.open(abs_path, "wb") as out_file:
            while True:
                chunk = await upload_file.read(64 * 1024)
                if not chunk:
                    break
                await out_file.write(chunk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save image: {str(e)}")

    return os.path.relpath(abs_path, start=os.getcwd())