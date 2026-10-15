import hashlib
from pathlib import Path
from typing import Tuple
from contract_app.bootstrap.config import settings

class FileStorage:
    def __init__(self, base_dir: Path = settings.storage_dir):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_file(self, content: bytes, file_name: str) -> Tuple[str, str]:
        content_hash = hashlib.sha256(content).hexdigest()
        ext = Path(file_name).suffix or ".docx"
        object_key = f"{content_hash}{ext}"
        target_path = self.base_dir / object_key
        if not target_path.exists():
            target_path.write_bytes(content)
        return object_key, content_hash

    def get_file_path(self, object_key: str) -> Path:
        return self.base_dir / object_key

    def read_file(self, object_key: str) -> bytes:
        target_path = self.get_file_path(object_key)
        if not target_path.exists():
            raise FileNotFoundError(f"File object not found: {object_key}")
        return target_path.read_bytes()

file_storage = FileStorage()
