from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from contract_app.infrastructure.persistence.repositories import repo_store
from contract_app.infrastructure.storage.file_storage import file_storage
from contract_app.infrastructure.editors.onlyoffice_adapter import onlyoffice_adapter
from contract_app.modules.documents.domain.session import EditorSession
from contract_app.modules.documents.domain.version import DocumentVersion
from contract_app.modules.documents.application.docx_service import docx_service
from contract_app.shared.ids import save_request_id

router = APIRouter(prefix="", tags=["editor-sessions"])

class CreateSessionRequest(BaseModel):
    contract_id: str
    version_id: Optional[str] = None
    provider: str = "onlyoffice"
    user_name: Optional[str] = "复核专员"

class SaveContentRequest(BaseModel):
    content_text: Optional[str] = None

@router.post("/editor-sessions")
async def create_editor_session(req: CreateSessionRequest, request: Request):
    contract = await repo_store.get_contract(req.contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    target_ver_id = req.version_id or contract.head_version_id
    version = await repo_store.get_version(target_ver_id or "")
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    session = EditorSession(
        contract_id=req.contract_id,
        base_version_id=version.id,
        provider=req.provider,
        document_key=f"doc_{version.id}_{version.content_hash[:8]}"
    )
    await repo_store.save_session(session)

    base_url = str(request.base_url).rstrip("/")
    download_url = f"{base_url}/api/documents/{version.id}/download"
    callback_url = f"{base_url}/api/editor-callbacks/{req.provider}"

    editor_config = onlyoffice_adapter.build_editor_config(
        document_key=session.document_key,
        file_name=f"{contract.title}.docx",
        download_url=download_url,
        callback_url=callback_url,
        user_name=req.user_name or "复核专员"
    )

    return {
        "session": session,
        "editor_config": editor_config,
        "document_key": session.document_key
    }

@router.get("/documents/{version_id}/download")
async def download_version_document(version_id: str):
    version = await repo_store.get_version(version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    file_path = file_storage.get_file_path(version.object_key)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File object not found")
    return FileResponse(
        path=str(file_path),
        filename=f"contract_{version_id}.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

@router.get("/documents/{version_id}/structure")
async def get_document_structure(version_id: str):
    version = await repo_store.get_version(version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    blocks = docx_service.extract_structure(version.object_key)
    return {
        "version_id": version.id,
        "blocks": blocks
    }

@router.post("/editor-sessions/{session_id}/save-requests")
async def create_save_request(session_id: str, body: Optional[SaveContentRequest] = None):
    session = await repo_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    req_id = save_request_id()
    contract = await repo_store.get_contract(session.contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    base_ver = await repo_store.get_version(session.base_version_id)
    if not base_ver:
        raise HTTPException(status_code=404, detail="Base version not found")

    # If web editor provided modified content, create new user_saved version
    if body and body.content_text:
        paras = body.content_text.strip().split("\n")
        new_key, new_hash = docx_service.create_sample_docx(contract.title, paras)
        new_ver = DocumentVersion(
            contract_id=contract.id,
            parent_id=base_ver.id,
            kind="user_saved",
            object_key=new_key,
            content_hash=new_hash,
            created_by="人工在线保存",
            summary="用户手动编辑并保存检查点"
        )
        await repo_store.save_version(new_ver)
        contract.advance_head(new_ver.id)
        await repo_store.save_contract(contract)
        session.advance_generation()
        session.save_checkpoint_id = new_ver.id
        await repo_store.save_session(session)
        return {
            "save_request_id": req_id,
            "status": "confirmed",
            "confirmed_version_id": new_ver.id
        }

    return {
        "save_request_id": req_id,
        "status": "confirmed",
        "confirmed_version_id": base_ver.id
    }

@router.post("/editor-callbacks/{provider}")
async def handle_editor_callback(provider: str, payload: dict):
    # Status 2: Document is ready for saving per ONLYOFFICE specs
    status = payload.get("status")
    download_url = payload.get("url")
    return {"error": 0}
