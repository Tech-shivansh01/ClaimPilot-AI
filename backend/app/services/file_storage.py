import os
import shutil
import uuid

from app.config import settings


def save_upload(claim_id: int, upload_file, doc_type: str) -> str:
    claim_dir = os.path.join(settings.UPLOAD_DIR, str(claim_id))
    os.makedirs(claim_dir, exist_ok=True)

    ext = os.path.splitext(upload_file.filename)[1]
    safe_name = f"{doc_type}_{uuid.uuid4().hex[:8]}{ext}"
    dest_path = os.path.join(claim_dir, safe_name)

    with open(dest_path, "wb") as f:
        shutil.copyfileobj(upload_file.file, f)

    return dest_path
