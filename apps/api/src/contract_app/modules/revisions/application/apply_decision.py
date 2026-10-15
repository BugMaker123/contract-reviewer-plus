from typing import List, Optional
from contract_app.shared.errors import VersionConflictError
from contract_app.infrastructure.persistence.repositories import repo_store
from contract_app.modules.revisions.domain.decision_command import DecisionCommand
from contract_app.modules.documents.domain.version import DocumentVersion
from contract_app.modules.documents.application.docx_service import docx_service

class ApplyDecisionUseCase:
    async def execute(
        self,
        contract_id: str,
        expected_version_id: str,
        operation_ids: List[str],
        action: str,  # accept, reject, reset
        idempotency_key: Optional[str] = None
    ) -> DecisionCommand:
        contract = await repo_store.get_contract(contract_id)
        if not contract:
            raise ValueError(f"Contract {contract_id} not found")

        # Invariant 6: All commands verify expected version
        if contract.head_version_id != expected_version_id:
            raise VersionConflictError(current_version_id=contract.head_version_id or "")

        cmd = DecisionCommand(
            contract_id=contract_id,
            expected_version_id=expected_version_id,
            operation_ids=operation_ids,
            action=action,
            idempotency_key=idempotency_key
        )
        cmd.mark_executing()

        curr_ver = await repo_store.get_version(expected_version_id)
        if not curr_ver:
            cmd.mark_failed("Current version not found")
            await repo_store.save_decision_command(cmd)
            return cmd

        # Find plan
        run = await repo_store.get_review_run(contract.latest_review_run_id or "")
        plan = None
        if run and run.plan_id:
            plan = await repo_store.get_revision_plan(run.plan_id)

        affected_issue_ids = set()
        if plan:
            for op_id in operation_ids:
                op = plan.get_operation(op_id)
                if op:
                    if action == "accept":
                        op.accept()
                    elif action == "reject":
                        op.reject()
                    else:
                        op.reset()
                    if op.issue_group_id:
                        affected_issue_ids.add(op.issue_group_id)
            await repo_store.save_revision_plan(plan)

        # Update affected issue group statuses
        if run:
            issues = await repo_store.get_issue_groups(run.id)
            for ig in issues:
                if ig.id in affected_issue_ids and plan:
                    ops = [o for o in plan.operations if o.issue_group_id == ig.id]
                    if ops:
                        acc = sum(1 for o in ops if o.status == "accepted")
                        rej = sum(1 for o in ops if o.status == "rejected")
                        if acc == len(ops):
                            ig.status = "accepted"
                        elif rej == len(ops):
                            ig.status = "rejected"
                        elif acc > 0:
                            ig.status = "partially_accepted"
                        else:
                            ig.status = "unreviewed"
            await repo_store.save_issue_groups(run.id, issues)

        # Generate verified revision version
        cmd.mark_awaiting_save()
        if plan:
            new_key, new_hash = docx_service.apply_revision_plan(curr_ver.object_key, plan, clean=False)
            new_ver = DocumentVersion(
                contract_id=contract_id,
                parent_id=curr_ver.id,
                kind="verified",
                object_key=new_key,
                content_hash=new_hash,
                created_by="复核专员",
                review_run_id=contract.latest_review_run_id,
                summary=f"已执行复核操作 ({action}: {len(operation_ids)} 处修订)",
                revision_count=sum(1 for o in plan.operations if o.status == "pending")
            )
            await repo_store.save_version(new_ver)
            contract.advance_head(new_ver.id)
            await repo_store.save_contract(contract)
            cmd.mark_confirmed(new_ver.id)
        else:
            cmd.mark_confirmed(curr_ver.id)

        await repo_store.save_decision_command(cmd)
        return cmd

apply_decision_use_case = ApplyDecisionUseCase()
