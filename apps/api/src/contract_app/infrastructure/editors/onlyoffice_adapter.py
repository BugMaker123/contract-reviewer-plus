from typing import Dict, Any, Optional
import hmac
import hashlib
import base64
import json
from contract_app.bootstrap.config import settings

class OnlyOfficeAdapter:
    def __init__(self):
        self.secret = settings.onlyoffice_secret
        self.public_url = settings.onlyoffice_public_url
        self.internal_url = settings.onlyoffice_internal_url

    def build_editor_config(
        self,
        document_key: str,
        file_name: str,
        download_url: str,
        callback_url: str,
        user_id: str = "user_1",
        user_name: str = "复核专员",
        mode: str = "edit"
    ) -> Dict[str, Any]:
        config: Dict[str, Any] = {
            "documentType": "word",
            "document": {
                "fileType": "docx",
                "key": document_key,
                "title": file_name,
                "url": download_url,
                "permissions": {
                    "download": True,
                    "edit": mode == "edit",
                    "print": True,
                    "review": True,
                    "comment": True
                }
            },
            "editorConfig": {
                "callbackUrl": callback_url,
                "lang": "zh-CN",
                "mode": mode,
                "user": {
                    "id": user_id,
                    "name": user_name
                },
                "customization": {
                    "autosave": False,
                    "forcesave": True,
                    "features": {
                        "spellcheck": False
                    },
                    "review": {
                        "reviewDisplay": "markup",
                        "trackChanges": True
                    }
                }
            }
        }
        if self.secret:
            config["token"] = self._generate_jwt(config)
        return config

    def _generate_jwt(self, payload: Dict[str, Any]) -> str:
        header = {"alg": "HS256", "typ": "JWT"}
        def b64_url(b: bytes) -> str:
            return base64.urlsafe_b64encode(b).decode('utf-8').rstrip('=')
        h_str = b64_url(json.dumps(header).encode('utf-8'))
        p_str = b64_url(json.dumps(payload).encode('utf-8'))
        msg = f"{h_str}.{p_str}".encode('utf-8')
        sig = hmac.new(self.secret.encode('utf-8'), msg, hashlib.sha256).digest()
        return f"{h_str}.{p_str}.{b64_url(sig)}"

onlyoffice_adapter = OnlyOfficeAdapter()
