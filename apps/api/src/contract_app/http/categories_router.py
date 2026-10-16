from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from contract_app.infrastructure.persistence.repositories import repo_store
from contract_app.modules.checklists.domain.category import BusinessCategory
from contract_app.shared.clock import now_iso

router = APIRouter(prefix="/categories", tags=["categories"])

class CreateCategoryReq(BaseModel):
    name: str
    code: str
    description: Optional[str] = ""
    sort_order: int = 1

class UpdateCategoryReq(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None

@router.get("")
async def list_categories(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = None
):
    items, total = await repo_store.list_categories_paged(page=page, page_size=page_size, keyword=keyword)
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.get("/all")
async def list_all_categories():
    items = await repo_store.list_all_categories()
    return {"items": items}

@router.post("")
async def create_category(req: CreateCategoryReq):
    category = BusinessCategory(
        name=req.name.strip(),
        code=req.code.strip().upper(),
        description=req.description or "",
        sort_order=req.sort_order
    )
    await repo_store.save_category(category)
    return {"category": category}

@router.put("/{cat_id}")
async def update_category(cat_id: str, req: UpdateCategoryReq):
    cat = await repo_store.get_category(cat_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    if req.name is not None:
        cat.name = req.name.strip()
    if req.code is not None:
        cat.code = req.code.strip().upper()
    if req.description is not None:
        cat.description = req.description
    if req.sort_order is not None:
        cat.sort_order = req.sort_order
    cat.updated_at = now_iso()
    await repo_store.save_category(cat)
    return {"category": cat}

@router.delete("/{cat_id}")
async def delete_category(cat_id: str):
    # Check if any checklist is bound to this category
    checklists, _ = await repo_store.list_checklists_paged(page=1, page_size=1, category_id=cat_id)
    if checklists:
        raise HTTPException(
            status_code=400,
            detail="该业务分类下仍有关联的审查清单规则，请先迁移或删除对应审查清单"
        )
    success = await repo_store.delete_category(cat_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"success": True, "deleted_id": cat_id}
