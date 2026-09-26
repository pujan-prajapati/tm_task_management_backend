import os
import uuid
import shutil
from fastapi import UploadFile

ALLOWED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}


# ============== UPLOAD FILE ===================
def save_file(
    file: UploadFile,
    folder: str,
    allowed_extensions: set[str] = ALLOWED_IMAGE_EXTENSIONS,
):
    extension = os.path.splitext(file.filename)[1].lower()

    if extension not in allowed_extensions:
        raise ValueError(
            f"File extension not allowed. " f"Allowed extensions: {allowed_extensions}"
        )

    os.makedirs(folder, exist_ok=True)

    filename = f"{uuid.uuid4()}{extension}"

    file_path = os.path.join(folder, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return filename


# ============== DELETE FILE ===================
def delete_file(filename: str, folder: str):
    file_path = os.path.join(folder, filename)

    if os.path.exists(file_path):
        os.remove(file_path)
