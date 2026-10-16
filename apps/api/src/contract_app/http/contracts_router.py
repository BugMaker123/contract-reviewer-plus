from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional, List
from contract_app.infrastructure.persistence.repositories import repo_store
from contract_app.infrastructure.storage.file_storage import file_storage
from contract_app.modules.contracts.domain.contract import Contract
from contract_app.modules.documents.domain.version import DocumentVersion
from contract_app.modules.documents.application.docx_service import docx_service

router = APIRouter(prefix="/contracts", tags=["contracts"])

SAMPLE_CONTRACT_TEXT = [
    "第一条（合作宗旨与服务范围）：甲方委托乙方进行新一代云原生企业数据资产中台的设计、定制化研发与系统上线支持服务。乙方应严格遵照技术规格书完成全部交付任务。",
    "第二条（价款与付款方式）：本合同总金额为人民币贰佰万元整（￥2,000,000.00）。款项分三期支付：签署后支付30%预付款；系统测试上线后支付50%；剩余20%质保金在上线后视情况另行协商支付时间。",
    "第三条（违约责任）：任何一方违约，应向守约方支付全部损失，包含直接与间接损失，且该赔偿责任不设上限。若乙方延迟交付，每日按合同总金额千分之五支付逾期违约金。",
    "第四条（知识产权归属）：在本合同履行期间产生的所有设计草案、源代码、技术文档及衍生发明专利等成果，其全部知识产权无偿转让并无条件归对方所有，包含签约前我方已有的既有知识产权。",
    "第五条（合同解除权）：在合同履行期限内，任何一方均有权在无需事先通知对方的情况下单方随时解除本合同，且无需承担违约及赔偿责任。",
    "第六条（争议解决）：因本合同履行引起的任何争议，双方应友好协商；协商不成的，应向对方所在地有管辖权的人民法院提起诉讼。"
]

import json

@router.post("")
async def create_contract(
    file: Optional[UploadFile] = File(None),
    title: Optional[str] = Form(None),
    stance: Optional[str] = Form("我方(受托方)"),
    category_id: Optional[str] = Form(None),
    category_name: Optional[str] = Form(None),
    checklist_ids: Optional[str] = Form(None),
    focus_areas: Optional[str] = Form(None)
):
    if not file:
        raise HTTPException(
            status_code=400,
            detail="必须上传合同文档（.docx 格式），请选择文件后再进入工作台"
        )

    file_name = file.filename or "contract.docx"
    if not file_name.lower().endswith(".docx"):
        raise HTTPException(
            status_code=400,
            detail="当前仅支持 Word (.docx) 格式文档。若为旧版 .doc 或其他格式，请另存为 .docx 后上传"
        )

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="上传的文件内容为空，请选择有效的合同文件")

    object_key, content_hash = file_storage.save_file(content, file_name)
    contract_title = title or file_name.rsplit(".", 1)[0]

    # Parse checklist IDs
    parsed_checklist_ids = []
    if checklist_ids:
        try:
            parsed_checklist_ids = json.loads(checklist_ids)
        except Exception:
            parsed_checklist_ids = [c.strip() for c in checklist_ids.split(",") if c.strip()]

    if not parsed_checklist_ids:
        raise HTTPException(
            status_code=400,
            detail="必须选择至少一项审查清单标准后再进入工作台"
        )

    # Parse focus areas
    parsed_focus_areas = []
    if focus_areas:
        try:
            parsed_focus_areas = json.loads(focus_areas)
        except Exception:
            parsed_focus_areas = [f.strip() for f in focus_areas.split(",") if f.strip()]

    # Auto resolve category_name if missing
    resolved_cat_name = category_name
    if category_id and not resolved_cat_name:
        cat = await repo_store.get_category(category_id)
        if cat:
            resolved_cat_name = cat.name

    # If focus areas not passed but checklist IDs are, auto-populate from checklist titles
    if parsed_checklist_ids and not parsed_focus_areas:
        for cid in parsed_checklist_ids:
            chk = await repo_store.get_checklist(cid)
            if chk:
                parsed_focus_areas.append(chk.title)

    contract = Contract(
        title=contract_title,
        stance=stance or "我方",
        category_id=category_id,
        category_name=resolved_cat_name,
        checklist_ids=parsed_checklist_ids,
        focus_areas=parsed_focus_areas
    )
    version = DocumentVersion(
        contract_id=contract.id,
        kind="original",
        object_key=object_key,
        content_hash=content_hash,
        created_by="系统初始上传",
        summary="原始上传合同快照"
    )
    contract.head_version_id = version.id

    await repo_store.save_version(version)
    await repo_store.save_contract(contract)
    return {
        "contract": contract,
        "initial_version": version
    }

@router.get("")
async def list_contracts(page: int = 1, page_size: int = 10, keyword: Optional[str] = None):
    items, total = await repo_store.list_contracts_paged(page=page, page_size=page_size, keyword=keyword)
    return {
        "contracts": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.delete("/{contract_id}")
async def delete_contract(contract_id: str):
    success = await repo_store.delete_contract(contract_id)
    if not success:
        raise HTTPException(status_code=404, detail="Contract not found")
    return {"success": True, "deleted_id": contract_id}

@router.get("/{contract_id}")
async def get_contract(contract_id: str):
    contract = await repo_store.get_contract(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    head_ver = await repo_store.get_version(contract.head_version_id or "")
    return {
        "contract": contract,
        "head_version": head_ver
    }

@router.get("/{contract_id}/versions")
async def list_contract_versions(contract_id: str):
    versions = await repo_store.list_versions_by_contract(contract_id)
    return {"versions": versions}

@router.post("/{contract_id}/verification")
async def complete_verification(contract_id: str):
    contract = await repo_store.get_contract(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    contract.review_status = "verified"
    await repo_store.save_contract(contract)
    return {"success": True, "contract": contract}

@router.post("/sample")
async def create_sample_contract_route(
    category_id: Optional[str] = Form(None),
    category_name: Optional[str] = Form(None),
    checklist_ids: Optional[str] = Form(None),
):
    contract_title = "软件定制开发与技术服务合作协议（标准业务样本）"
    object_key, content_hash = docx_service.create_sample_docx(contract_title, SAMPLE_CONTRACT_TEXT)
    parsed_checklist_ids = ["chk_001", "chk_002", "chk_003"]
    if checklist_ids:
        try:
            parsed_checklist_ids = json.loads(checklist_ids)
        except Exception:
            parsed_checklist_ids = [c.strip() for c in checklist_ids.split(",") if c.strip()]
    contract = Contract(
        title=contract_title,
        stance="我方(受托方)",
        category_id=category_id or "cat_tech",
        category_name=category_name or "技术开发与实施类",
        checklist_ids=parsed_checklist_ids,
        focus_areas=["付款节点与验收先决条件明确", "违约金责任上限与直接损失界定", "既有背景知识产权及衍生权属保留"]
    )
    version = DocumentVersion(
        contract_id=contract.id,
        kind="original",
        object_key=object_key,
        content_hash=content_hash,
        created_by="系统初始样本",
        summary="原始示例合同快照"
    )
    contract.head_version_id = version.id
    await repo_store.save_version(version)
    await repo_store.save_contract(contract)
    return {"contract": contract, "initial_version": version}
