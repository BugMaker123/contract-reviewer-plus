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

from contract_app.shared.errors import ReviewCancelledError, ReviewTimeoutError
from contract_app.infrastructure.events.event_bus import event_bus
from contract_app.infrastructure.persistence.repositories import repo_store
from contract_app.modules.reviews.domain.review_state import ReviewStatus
from contract_app.modules.reviews.application.graph.review_graph import review_graph_app

class RunPipelineUseCase:
    async def execute(self, run_id: str):
        run = await repo_store.get_review_run(run_id)
        if not run:
            return

        initial_state = {
            "run_id": run.id,
            "contract_id": run.contract_id,
            "input_version_id": run.input_version_id,
            "stance": run.stance,
            "focus_areas": run.focus_areas,
            "attempt": run.attempt,
            "blocks": [],
            "raw_findings": [],
            "valid_findings": [],
            "issue_groups": []
        }

        try:
            # 执行编译后的 LangGraph 状态图工作流
            final_state = await review_graph_app.ainvoke(initial_state)
            if final_state.get("error"):
                raise RuntimeError(final_state["error"])
        except ReviewCancelledError:
            run.status = ReviewStatus.CANCELLED
            await repo_store.save_review_run(run)
            await event_bus.publish(run.id, "cancelled", {"run_id": run.id, "message": "任务已取消"}, attempt=run.attempt)
        except Exception as e:
            run.fail("PIPELINE_ERROR", str(e))
            await repo_store.save_review_run(run)
            await event_bus.publish(run.id, "failed", {"run_id": run.id, "error": str(e)}, attempt=run.attempt)

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
