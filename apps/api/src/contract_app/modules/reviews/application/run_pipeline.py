import asyncio
from datetime import datetime
from typing import List, Dict, Any
from contract_app.shared.clock import now_utc
from contract_app.shared.errors import ReviewCancelledError, ReviewTimeoutError
from contract_app.infrastructure.events.event_bus import event_bus
from contract_app.infrastructure.persistence.repositories import repo_store
from contract_app.infrastructure.models.model_gateway import model_gateway
from contract_app.modules.reviews.domain.review_run import ReviewRun
from contract_app.modules.reviews.domain.review_state import PipelineStage, ReviewStatus
from contract_app.modules.documents.domain.version import DocumentVersion
from contract_app.modules.documents.application.docx_service import docx_service
from contract_app.modules.issues.domain.issue_group import IssueGroup
from contract_app.modules.revisions.domain.revision_plan import RevisionPlan
from contract_app.modules.revisions.domain.operation import RevisionOperation

class RunPipelineUseCase:
    async def execute(self, run_id: str):
        run = await repo_store.get_review_run(run_id)
        if not run:
            return

        try:
            # Stage 1: prepare_snapshot
            await self._step_start(run, PipelineStage.PREPARE_SNAPSHOT, "准备不可变审查快照")
            version = await repo_store.get_version(run.input_version_id)
            if not version:
                raise ValueError(f"Input version {run.input_version_id} not found")
            await asyncio.sleep(0.3)
            await self._step_done(run, PipelineStage.PREPARE_SNAPSHOT)

            # Stage 2: build_context
            await self._step_start(run, PipelineStage.BUILD_CONTEXT, "提取合同条款结构与上下文")
            blocks = docx_service.extract_structure(version.object_key)
            await asyncio.sleep(0.4)
            await self._step_done(run, PipelineStage.BUILD_CONTEXT, {"block_count": len(blocks)})

            # Stage 3: analyze_clauses
            await self._step_start(run, PipelineStage.ANALYZE_CLAUSES, "多维度条款风险分析")
            raw_findings = await model_gateway.analyze_blocks(blocks, run.stance, run.focus_areas)

            # Publish streaming provisional public summaries
            for idx, f in enumerate(raw_findings):
                self._check_cancellation_and_deadline(run)
                await event_bus.publish(
                    run.id,
                    "analysis_provisional",
                    {
                        "item_id": f"draft_{idx+1}",
                        "clause_id": f["clause_id"],
                        "title": f["title"],
                        "severity": f["severity"],
                        "evidence": f["evidence"],
                        "public_analysis": f["public_analysis"],
                        "proposal": f["proposal"],
                        "provisional": True
                    },
                    attempt=run.attempt
                )
                await asyncio.sleep(0.15)
            await self._step_done(run, PipelineStage.ANALYZE_CLAUSES, {"finding_count": len(raw_findings)})

            # Stage 4: validate_findings
            await self._step_start(run, PipelineStage.VALIDATE_FINDINGS, "校验原文依据与改写边界")
            valid_findings = [f for f in raw_findings if f.get("evidence") and f.get("title")]
            await asyncio.sleep(0.2)
            await self._step_done(run, PipelineStage.VALIDATE_FINDINGS)

            # Stage 5: consolidate_issues
            await self._step_start(run, PipelineStage.CONSOLIDATE_ISSUES, "归并条款级问题组")
            issue_groups: List[IssueGroup] = []
            for idx, vf in enumerate(valid_findings):
                ig = IssueGroup(
                    run_id=run.id,
                    clause_title=vf["clause_id"],
                    severity=vf["severity"],
                    risk_points=[vf["title"]],
                    evidence=vf["evidence"],
                    public_analysis=vf["public_analysis"],
                    proposal=vf["proposal"],
                    anchors=[vf["evidence"][:30]]
                )
                issue_groups.append(ig)
            await repo_store.save_issue_groups(run.id, issue_groups)
            await asyncio.sleep(0.2)
            await self._step_done(run, PipelineStage.CONSOLIDATE_ISSUES, {"group_count": len(issue_groups)})

            # Stage 6: compose_revisions
            await self._step_start(run, PipelineStage.COMPOSE_REVISIONS, "组装原生修订操作与建议文档")
            plan = RevisionPlan(review_run_id=run.id, base_version_id=version.id)
            for idx, vf in enumerate(valid_findings):
                op = RevisionOperation(
                    plan_id=plan.id,
                    issue_group_id=issue_groups[idx].id if idx < len(issue_groups) else "",
                    kind="replace",
                    anchor=vf["clause_id"],
                    expected_text=vf.get("expected_text", vf["evidence"]),
                    replacement_text=vf.get("replacement_text", vf["evidence"]),
                    public_reason=vf["proposal"]
                )
                plan.operations.append(op)
            await repo_store.save_revision_plan(plan)

            # Generate proposed version DOCX
            prop_key, prop_hash = docx_service.apply_revision_plan(version.object_key, plan, clean=False)
            ai_version = DocumentVersion(
                contract_id=run.contract_id,
                parent_id=version.id,
                kind="ai_proposal",
                object_key=prop_key,
                content_hash=prop_hash,
                created_by="系统合规审查",
                review_run_id=run.id,
                summary=f"审查修订建议稿 (包含 {len(plan.operations)} 处建议修改)",
                revision_count=len(plan.operations)
            )
            await repo_store.save_version(ai_version)
            await self._step_done(run, PipelineStage.COMPOSE_REVISIONS, {"plan_id": plan.id})

            # Stage 7: publish_result
            await self._step_start(run, PipelineStage.PUBLISH_RESULT, "发布审查成果并同步工作副本")
            run.succeed(result_version_id=ai_version.id, plan_id=plan.id)
            await repo_store.save_review_run(run)

            # Update contract
            contract = await repo_store.get_contract(run.contract_id)
            if contract:
                contract.set_review_run(run.id)
                contract.advance_head(ai_version.id)
                contract.review_status = "reviewed"
                await repo_store.save_contract(contract)

            await event_bus.publish(
                run.id,
                "succeeded",
                {
                    "run_id": run.id,
                    "result_version_id": ai_version.id,
                    "plan_id": plan.id,
                    "issue_count": len(issue_groups),
                    "revision_count": len(plan.operations)
                },
                attempt=run.attempt
            )

        except ReviewCancelledError:
            run.status = ReviewStatus.CANCELLED
            await repo_store.save_review_run(run)
            await event_bus.publish(run.id, "cancelled", {"run_id": run.id, "message": "任务已取消"})
        except Exception as e:
            run.fail("PIPELINE_ERROR", str(e))
            await repo_store.save_review_run(run)
            await event_bus.publish(run.id, "failed", {"run_id": run.id, "error": str(e)})

    def _check_cancellation_and_deadline(self, run: ReviewRun):
        if run.is_cancelled():
            raise ReviewCancelledError(run.id)
        if now_utc() >= run.deadline:
            raise ReviewTimeoutError(run.id)

    async def _step_start(self, run: ReviewRun, stage: PipelineStage, desc: str):
        self._check_cancellation_and_deadline(run)
        run.advance_stage(stage)
        await repo_store.save_review_run(run)
        await event_bus.publish(run.id, "stage_started", {"stage": stage.value, "description": desc}, attempt=run.attempt)

    async def _step_done(self, run: ReviewRun, stage: PipelineStage, payload: dict = None):
        self._check_cancellation_and_deadline(run)
        p = {"stage": stage.value}
        if payload:
            p.update(payload)
        await event_bus.publish(run.id, "stage_completed", p, attempt=run.attempt)

run_pipeline_use_case = RunPipelineUseCase()
