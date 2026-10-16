import asyncio
from fastapi import APIRouter, HTTPException, Request, Header, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
from contract_app.infrastructure.persistence.repositories import repo_store
from contract_app.infrastructure.events.event_bus import event_bus
from contract_app.modules.reviews.domain.review_run import ReviewRun
from contract_app.modules.reviews.domain.review_state import ReviewStatus
from contract_app.modules.reviews.application.run_pipeline import run_pipeline_use_case

router = APIRouter(prefix="", tags=["reviews"])

class StartReviewRequest(BaseModel):
    contract_id: str
    input_version_id: Optional[str] = None
    stance: Optional[str] = "我方"
    focus_areas: Optional[List[str]] = None

class AddCommentRequest(BaseModel):
    author: str = "复核专员"
    content: str

class FollowupRequest(BaseModel):
    question: str

@router.post("/review-runs", status_code=202)
async def start_review_run(req: StartReviewRequest, background_tasks: BackgroundTasks):
    contract = await repo_store.get_contract(req.contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    target_ver_id = req.input_version_id or contract.head_version_id
    version = await repo_store.get_version(target_ver_id or "")
    if not version:
        raise HTTPException(status_code=404, detail="Input version not found")

    run = ReviewRun(
        contract_id=req.contract_id,
        input_version_id=version.id,
        stance=req.stance or contract.stance,
        focus_areas=req.focus_areas or contract.focus_areas or ["违约责任", "单方解约", "知识产权", "付款条件"]
    )
    await repo_store.save_review_run(run)
    contract.set_review_run(run.id)
    await repo_store.save_contract(contract)

    # Dispatch to worker / background pipeline
    background_tasks.add_task(run_pipeline_use_case.execute, run.id)

    return {
        "run_id": run.id,
        "status": run.status.value,
        "contract_id": run.contract_id,
        "input_version_id": run.input_version_id
    }

@router.get("/review-runs/{run_id}")
async def get_review_run(run_id: str):
    run = await repo_store.get_review_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Review run not found")
    plan = await repo_store.get_revision_plan(run.plan_id or "") if run.plan_id else None
    return {
        "run": run,
        "plan": plan
    }

@router.get("/review-runs/{run_id}/events")
async def subscribe_review_events(
    run_id: str,
    last_event_id: Optional[str] = Header(None, alias="Last-Event-ID")
):
    run = await repo_store.get_review_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Review run not found")

    start_cursor = int(last_event_id) if last_event_id and last_event_id.isdigit() else None
    stream = event_bus.subscribe(run_id, start_cursor)
    return StreamingResponse(
        stream,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.post("/review-runs/{run_id}/cancel")
async def cancel_review_run(run_id: str):
    run = await repo_store.get_review_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Review run not found")
    run.request_cancel()
    await repo_store.save_review_run(run)
    return {"run_id": run.id, "status": run.status.value}

@router.get("/review-runs/{run_id}/issue-groups")
async def list_issue_groups(run_id: str):
    run = await repo_store.get_review_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Review run not found")
    issues = await repo_store.get_issue_groups(run_id)
    plan = await repo_store.get_revision_plan(run.plan_id or "") if run.plan_id else None
    return {
        "issue_groups": issues,
        "plan": plan
    }

@router.post("/issue-groups/{issue_id}/comments")
async def add_issue_comment(issue_id: str, req: AddCommentRequest):
    # Find issue group across runs
    for run in repo_store.review_runs.values():
        ig = await repo_store.get_issue_group(run.id, issue_id)
        if ig:
            ig.add_comment(req.author, req.content)
            await repo_store.save_issue_groups(run.id, await repo_store.get_issue_groups(run.id))
            return {"success": True, "comments": ig.comments}
    raise HTTPException(status_code=404, detail="Issue group not found")

@router.post("/issue-groups/{issue_id}/followups")
async def followup_issue(issue_id: str, req: FollowupRequest):
    for run in repo_store.review_runs.values():
        ig = await repo_store.get_issue_group(run.id, issue_id)
        if ig:
            answer = (
                f"针对【{ig.clause_title}】提出的追问「{req.question}」：\n"
                f"在当前【{run.stance}】立场下，若对方坚决不肯接受全额删除该款，"
                f"可采用替代性商务方案：在保留对方监督权的同时，将我方赔偿义务限定为直接过错，并增加第三方审计作为前置条件。"
            )
            ig.add_followup(req.question, answer)
            await repo_store.save_issue_groups(run.id, await repo_store.get_issue_groups(run.id))
            return {"success": True, "followup": ig.followups[-1]}
    raise HTTPException(status_code=404, detail="Issue group not found")
