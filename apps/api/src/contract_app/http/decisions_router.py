from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import List, Optional
from contract_app.shared.errors import VersionConflictError
from contract_app.infrastructure.persistence.repositories import repo_store
from contract_app.modules.revisions.application.apply_decision import apply_decision_use_case

router = APIRouter(prefix="/decision-commands", tags=["decisions"])

class ApplyDecisionRequest(BaseModel):
    contract_id: str
    expected_version_id: str
    operation_ids: List[str]
    action: str = "accept"  # accept, reject, reset
    idempotency_key: Optional[str] = None

@router.post("")
async def create_decision_command(
    req: ApplyDecisionRequest,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")
):
    key = req.idempotency_key or idempotency_key
    try:
        cmd = await apply_decision_use_case.execute(
            contract_id=req.contract_id,
            expected_version_id=req.expected_version_id,
            operation_ids=req.operation_ids,
            action=req.action,
            idempotency_key=key
        )
        return {"command": cmd}
    except VersionConflictError as e:
        raise HTTPException(
            status_code=409,
            detail={
                "error": {
                    "code": e.code,
                    "message": e.message,
                    "details": e.details
                }
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{command_id}")
async def get_decision_command(command_id: str):
    cmd = await repo_store.get_decision_command(command_id)
    if not cmd:
        raise HTTPException(status_code=404, detail="Decision command not found")
    return {"command": cmd}
