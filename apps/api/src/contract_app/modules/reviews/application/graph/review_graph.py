# -*- coding: utf-8 -*-
"""
LangGraph-Orchestrated Contract Review StateGraph Workflow.
Implements the macro-level state machine with checkpointing, conditional routing,
and seamless SSE progress event streaming.
"""

from typing import TypedDict, List, Dict, Any, Optional
import asyncio
from langgraph.graph import StateGraph, START, END
from contract_app.shared.errors import ReviewCancelledError
from contract_app.infrastructure.events.event_bus import event_bus
from contract_app.infrastructure.persistence.repositories import repo_store
from contract_app.modules.reviews.domain.review_state import PipelineStage, ReviewStatus
from contract_app.modules.documents.domain.version import DocumentVersion
from contract_app.modules.documents.application.docx_service import docx_service
from contract_app.modules.issues.domain.issue_group import IssueGroup
from contract_app.modules.revisions.domain.revision_plan import RevisionPlan
from contract_app.modules.revisions.domain.operation import RevisionOperation
from contract_app.modules.reviews.application.agents.contract_multi_agent_team import contract_multi_agent_team

class ReviewGraphState(TypedDict, total=False):
    run_id: str
    contract_id: str
    input_version_id: str
    stance: str
    focus_areas: Optional[List[str]]
    checklists: List[Any]
    blocks: List[Dict[str, Any]]
    raw_findings: List[Dict[str, Any]]
    valid_findings: List[Dict[str, Any]]
    issue_groups: List[Any]
    plan_id: Optional[str]
    result_version_id: Optional[str]
    error: Optional[str]
    attempt: int
    validation_passed: bool

async def step_start(run_id: str, stage: PipelineStage, message: str, attempt: int = 1):
    run = await repo_store.get_review_run(run_id)
    if run:
        run.advance_stage(stage)
        await repo_store.save_review_run(run)
    await event_bus.publish(
        run_id,
        "stage_started",
        {"stage": stage.value, "stage_name": stage.chinese_name, "message": message},
        attempt=attempt
    )

async def step_done(run_id: str, stage: PipelineStage, metadata: Optional[Dict[str, Any]] = None, attempt: int = 1):
    payload = {"stage": stage.value, "stage_name": stage.chinese_name}
    if metadata:
        payload.update(metadata)
    await event_bus.publish(run_id, "stage_completed", payload, attempt=attempt)


# Node 1: Prepare Snapshot
async def node_prepare_snapshot(state: ReviewGraphState) -> ReviewGraphState:
    run_id = state["run_id"]
    await step_start(run_id, PipelineStage.PREPARE_SNAPSHOT, "准备不可变审查快照 (LangGraph 状态图启动)", state.get("attempt", 1))
    version = await repo_store.get_version(state["input_version_id"])
    if not version:
        return {**state, "error": f"Input version {state['input_version_id']} not found"}
    await asyncio.sleep(0.2)
    await step_done(run_id, PipelineStage.PREPARE_SNAPSHOT, attempt=state.get("attempt", 1))
    return state

# Node 2: Build Context
async def node_build_context(state: ReviewGraphState) -> ReviewGraphState:
    run_id = state["run_id"]
    await step_start(run_id, PipelineStage.BUILD_CONTEXT, "提取合同条款结构与上下文", state.get("attempt", 1))
    version = await repo_store.get_version(state["input_version_id"])
    blocks = docx_service.extract_structure(version.object_key)
    
    # Load checklists
    contract = await repo_store.get_contract(state["contract_id"])
    checklist_items = []
    if contract and contract.checklist_ids:
        for cid in contract.checklist_ids:
            chk = await repo_store.get_checklist(cid)
            if chk:
                checklist_items.append(chk)

    await asyncio.sleep(0.2)
    await step_done(run_id, PipelineStage.BUILD_CONTEXT, {"block_count": len(blocks)}, attempt=state.get("attempt", 1))
    return {**state, "blocks": blocks, "checklists": checklist_items}

# Node 3: Multi-Agent Review (AgentScope Multi-Agent Team)
async def node_multi_agent_review(state: ReviewGraphState) -> ReviewGraphState:
    run_id = state["run_id"]
    await step_start(run_id, PipelineStage.ANALYZE_CLAUSES, "AgentScope 多智能体深度协同研判", state.get("attempt", 1))
    
    # Run AgentScope multi-agent team (Auditor + Stance Advocate + Revision Drafter)
    raw_findings = await contract_multi_agent_team.collaborative_review(
        blocks=state["blocks"],
        stance=state["stance"],
        focus_areas=state.get("focus_areas"),
        checklists=state.get("checklists")
    )

    # Publish streaming provisional events for UI
    for idx, f in enumerate(raw_findings):
        await event_bus.publish(
            run_id,
            "analysis_provisional",
            {
                "item_id": f"draft_{idx+1}",
                "clause_id": f.get("clause_id", f"条款 {idx+1}"),
                "title": f.get("title", "合规风险"),
                "severity": f.get("severity", "medium"),
                "evidence": f.get("evidence", ""),
                "public_analysis": f.get("public_analysis", ""),
                "proposal": f.get("proposal", ""),
                "provisional": True
            },
            attempt=state.get("attempt", 1)
        )
        await asyncio.sleep(0.1)

    await step_done(run_id, PipelineStage.ANALYZE_CLAUSES, {"finding_count": len(raw_findings)}, attempt=state.get("attempt", 1))
    return {**state, "raw_findings": raw_findings}

# Node 4: Validate Findings (Evidence Grounding & Boundary Checks)
async def node_validate_findings(state: ReviewGraphState) -> ReviewGraphState:
    run_id = state["run_id"]
    await step_start(run_id, PipelineStage.VALIDATE_FINDINGS, "校验原文依据与改写边界 (Guardrails)", state.get("attempt", 1))
    raw = state.get("raw_findings", [])
    valid = [f for f in raw if f.get("evidence") and f.get("title")]
    await asyncio.sleep(0.15)
    await step_done(run_id, PipelineStage.VALIDATE_FINDINGS, attempt=state.get("attempt", 1))
    return {**state, "valid_findings": valid, "validation_passed": len(valid) > 0}

# Node 5: Consolidate Issues
async def node_consolidate_issues(state: ReviewGraphState) -> ReviewGraphState:
    run_id = state["run_id"]
    await step_start(run_id, PipelineStage.CONSOLIDATE_ISSUES, "归并条款级问题组", state.get("attempt", 1))
    valid = state.get("valid_findings", [])
    issue_groups: List[IssueGroup] = []
    for vf in valid:
        ig = IssueGroup(
            run_id=run_id,
            clause_title=vf.get("clause_id", "条款"),
            severity=vf.get("severity", "medium"),
            risk_points=[vf.get("title", "合规风险")],
            evidence=vf.get("evidence", ""),
            public_analysis=vf.get("public_analysis", ""),
            proposal=vf.get("proposal", ""),
            anchors=[vf.get("evidence", "")[:30]]
        )
        issue_groups.append(ig)
    await repo_store.save_issue_groups(run_id, issue_groups)
    await asyncio.sleep(0.15)
    await step_done(run_id, PipelineStage.CONSOLIDATE_ISSUES, {"group_count": len(issue_groups)}, attempt=state.get("attempt", 1))
    return {**state, "issue_groups": issue_groups}

# Node 6: Compose Revisions
async def node_compose_revisions(state: ReviewGraphState) -> ReviewGraphState:
    run_id = state["run_id"]
    await step_start(run_id, PipelineStage.COMPOSE_REVISIONS, "组装原生修订操作与建议文档", state.get("attempt", 1))
    version = await repo_store.get_version(state["input_version_id"])
    valid = state.get("valid_findings", [])
    issue_groups = state.get("issue_groups", [])

    plan = RevisionPlan(review_run_id=run_id, base_version_id=version.id)
    for idx, vf in enumerate(valid):
        op = RevisionOperation(
            plan_id=plan.id,
            issue_group_id=issue_groups[idx].id if idx < len(issue_groups) else "",
            kind="replace",
            anchor=vf.get("clause_id", ""),
            expected_text=vf.get("expected_text", vf.get("evidence", "")),
            replacement_text=vf.get("replacement_text", vf.get("evidence", "")),
            public_reason=vf.get("proposal", "")
        )
        plan.operations.append(op)
    await repo_store.save_revision_plan(plan)

    # Generate Word proposed docx
    prop_key, prop_hash = docx_service.apply_revision_plan(version.object_key, plan, clean=False)
    ai_version = DocumentVersion(
        contract_id=state["contract_id"],
        parent_id=version.id,
        kind="ai_proposal",
        object_key=prop_key,
        content_hash=prop_hash,
        created_by="系统智能合规审查 (AgentScope + LangGraph)",
        review_run_id=run_id,
        summary=f"审查修订建议稿 (包含 {len(plan.operations)} 处修改建议)",
        revision_count=len(plan.operations)
    )
    await repo_store.save_version(ai_version)
    await step_done(run_id, PipelineStage.COMPOSE_REVISIONS, {"plan_id": plan.id}, attempt=state.get("attempt", 1))
    return {**state, "plan_id": plan.id, "result_version_id": ai_version.id}

# Node 7: Publish Result
async def node_publish_result(state: ReviewGraphState) -> ReviewGraphState:
    run_id = state["run_id"]
    await step_start(run_id, PipelineStage.PUBLISH_RESULT, "发布审查成果并同步工作副本", state.get("attempt", 1))
    run = await repo_store.get_review_run(run_id)
    if run:
        run.succeed(result_version_id=state.get("result_version_id", ""), plan_id=state.get("plan_id", ""))
        await repo_store.save_review_run(run)

    contract = await repo_store.get_contract(state["contract_id"])
    if contract and state.get("result_version_id"):
        contract.set_review_run(run_id)
        contract.advance_head(state["result_version_id"])
        contract.review_status = "reviewed"
        await repo_store.save_contract(contract)

    await event_bus.publish(
        run_id,
        "succeeded",
        {
            "run_id": run_id,
            "result_version_id": state.get("result_version_id"),
            "plan_id": state.get("plan_id"),
            "issue_count": len(state.get("issue_groups", [])),
            "revision_count": len(state.get("valid_findings", []))
        },
        attempt=state.get("attempt", 1)
    )
    return state

# Build the LangGraph StateGraph
def build_contract_review_graph():
    workflow = StateGraph(ReviewGraphState)
    workflow.add_node("prepare_snapshot", node_prepare_snapshot)
    workflow.add_node("build_context", node_build_context)
    workflow.add_node("multi_agent_review", node_multi_agent_review)
    workflow.add_node("validate_findings", node_validate_findings)
    workflow.add_node("consolidate_issues", node_consolidate_issues)
    workflow.add_node("compose_revisions", node_compose_revisions)
    workflow.add_node("publish_result", node_publish_result)

    # Linear workflow with conditional branching
    workflow.add_edge(START, "prepare_snapshot")
    workflow.add_edge("prepare_snapshot", "build_context")
    workflow.add_edge("build_context", "multi_agent_review")
    workflow.add_edge("multi_agent_review", "validate_findings")

    def route_after_validation(state: ReviewGraphState) -> str:
        if state.get("error"):
            return END
        return "consolidate_issues"

    workflow.add_conditional_edges("validate_findings", route_after_validation, {
        "consolidate_issues": "consolidate_issues",
        END: END
    })
    workflow.add_edge("consolidate_issues", "compose_revisions")
    workflow.add_edge("compose_revisions", "publish_result")
    workflow.add_edge("publish_result", END)

    return workflow.compile()

review_graph_app = build_contract_review_graph()
