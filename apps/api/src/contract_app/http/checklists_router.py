from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Literal
from contract_app.infrastructure.persistence.repositories import repo_store
from contract_app.modules.checklists.domain.checklist_item import ChecklistItem
from contract_app.shared.clock import now_iso

router = APIRouter(prefix="/checklists", tags=["checklists"])

class CreateChecklistReq(BaseModel):
    category_id: str
    title: str
    risk_level: Literal["high", "medium", "low"] = "high"
    standard_clause: Optional[str] = ""
    check_prompt: Optional[str] = ""
    prompt_template: Optional[str] = ""
    is_enabled: bool = True
    sort_order: int = 1

class UpdateChecklistReq(BaseModel):
    category_id: Optional[str] = None
    title: Optional[str] = None
    risk_level: Optional[Literal["high", "medium", "low"]] = None
    standard_clause: Optional[str] = None
    check_prompt: Optional[str] = None
    prompt_template: Optional[str] = None
    is_enabled: Optional[bool] = None
    sort_order: Optional[int] = None

@router.get("")
async def list_checklists(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    category_id: Optional[str] = None,
    keyword: Optional[str] = None
):
    items, total = await repo_store.list_checklists_paged(
        page=page, page_size=page_size, category_id=category_id, keyword=keyword
    )
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.get("/{item_id}")
async def get_checklist(item_id: str):
    item = await repo_store.get_checklist(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    return {"item": item}

@router.post("")
async def create_checklist(req: CreateChecklistReq):
    category = await repo_store.get_category(req.category_id)
    if not category:
        raise HTTPException(status_code=400, detail="所选业务分类不存在，无法绑定")

    item = ChecklistItem(
        category_id=req.category_id,
        category_name=category.name,
        title=req.title.strip(),
        risk_level=req.risk_level,
        standard_clause=req.standard_clause or "",
        check_prompt=req.check_prompt or "",
        prompt_template=req.prompt_template or "",
        is_enabled=req.is_enabled,
        sort_order=req.sort_order
    )
    await repo_store.save_checklist(item)
    return {"item": item}

@router.put("/{item_id}")
async def update_checklist(item_id: str, req: UpdateChecklistReq):
    item = await repo_store.get_checklist(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")

    if req.category_id is not None:
        cat = await repo_store.get_category(req.category_id)
        if not cat:
            raise HTTPException(status_code=400, detail="目标业务分类不存在")
        item.category_id = cat.id
        item.category_name = cat.name

    if req.title is not None:
        item.title = req.title.strip()
    if req.risk_level is not None:
        item.risk_level = req.risk_level
    if req.standard_clause is not None:
        item.standard_clause = req.standard_clause
    if req.check_prompt is not None:
        item.check_prompt = req.check_prompt
    if req.prompt_template is not None:
        item.prompt_template = req.prompt_template
    if req.is_enabled is not None:
        item.is_enabled = req.is_enabled
    if req.sort_order is not None:
        item.sort_order = req.sort_order
    item.updated_at = now_iso()
    await repo_store.save_checklist(item)
    return {"item": item}

@router.delete("/{item_id}")
async def delete_checklist(item_id: str):
    success = await repo_store.delete_checklist(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    return {"success": True, "deleted_id": item_id}
