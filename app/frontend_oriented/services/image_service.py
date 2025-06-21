import os
import shutil
import uuid
from fastapi import HTTPException, UploadFile
from datetime import datetime




import aiofiles

async def save_upload_file(
    upload_file: UploadFile,
    patient_id: int,
    eye: str,
    date: str,
    upload_dir: str = "static/original_images"
) -> str:
    if not upload_file or not upload_file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file is not an image")

    ext = os.path.splitext(upload_file.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]:
        ext = ".png"  # fallback na .png

    try:
        parsed_date = datetime.strptime(date, "%d.%m.%Y").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format, expected DD.MM.YYYY")

    # Priprav bezpečný identifikátor
    safe_eye = "L" if eye.lower().startswith("l") else "R"
    safe_date = parsed_date.isoformat()  # napr. 2025-06-20
    unique_suffix = f"{uuid.uuid4().hex}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"  # 32 znakov + timestamp

    # Vytvor bezpečný názov súboru
    filename = f"{patient_id}_{safe_eye}_{safe_date}_{unique_suffix}{ext}"

    os.makedirs(upload_dir, exist_ok=True)
    abs_path = os.path.join(upload_dir, filename)

    try:
        async with aiofiles.open(abs_path, "wb") as out_file:
            while True:
                chunk = await upload_file.read(64 * 1024)
                if not chunk:
                    break
                await out_file.write(chunk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save image: {str(e)}")

    # relatívna cesta (napr. static/original_images/123_L_2025-06-20_abc123456_20250620235900.png)
    rel_path = os.path.relpath(abs_path, start=os.getcwd())
    url_path = rel_path.replace("\\", "/")  # prepni spätné lomky na lomky
    return url_path