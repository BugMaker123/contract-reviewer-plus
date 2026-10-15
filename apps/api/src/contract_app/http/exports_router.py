from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from contract_app.infrastructure.persistence.repositories import repo_store
from contract_app.infrastructure.storage.file_storage import file_storage
from contract_app.modules.exports.application.create_export import create_export_use_case

router = APIRouter(prefix="/exports", tags=["exports"])

class CreateExportRequest(BaseModel):
    contract_id: str
    kind: str = "clean_draft"  # clean_draft, track_changes, review_report

@router.post("")
async def create_export(req: CreateExportRequest):
    try:
        job = await create_export_use_case.execute(req.contract_id, req.kind)
        return {"export_job": job}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{export_id}")
async def get_export(export_id: str):
    job = await repo_store.get_export_job(export_id)
    if not job:
        raise HTTPException(status_code=404, detail="Export job not found")
    return {"export_job": job}

@router.get("/{export_id}/download")
async def download_export(export_id: str):
    job = await repo_store.get_export_job(export_id)
    if not job or not job.artifact_key:
        raise HTTPException(status_code=404, detail="Export artifact not found")
    file_path = file_storage.get_file_path(job.artifact_key)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Artifact file missing")
    return FileResponse(
        path=str(file_path),
        filename=job.file_name or f"export_{job.id}.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
