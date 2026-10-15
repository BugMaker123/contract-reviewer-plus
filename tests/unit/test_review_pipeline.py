import pytest
import sys
from pathlib import Path

# Add src to sys.path
src_dir = Path(__file__).resolve().parents[2] / "apps" / "api" / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from contract_app.modules.contracts.domain.contract import Contract
from contract_app.modules.documents.domain.version import DocumentVersion
from contract_app.modules.documents.application.docx_service import docx_service
from contract_app.modules.reviews.domain.review_run import ReviewRun
from contract_app.modules.reviews.domain.review_state import ReviewStatus
from contract_app.modules.reviews.application.run_pipeline import run_pipeline_use_case
from contract_app.modules.revisions.application.apply_decision import apply_decision_use_case
from contract_app.infrastructure.persistence.repositories import repo_store

@pytest.mark.asyncio
async def test_full_review_and_decision_lifecycle():
    # 1. Create sample contract docx
    paras = [
        "第一条：双方达成战略合作协议。",
        "第二条：任何一方违约，应向守约方赔偿全部损失，且责任不设上限。",
        "第三条：在合同期内，任何一方可单方随时解除合同，无需通知对方。"
    ]
    key, content_hash = docx_service.create_sample_docx("测试软件协议", paras)
    contract = Contract(title="测试软件协议")
    v1 = DocumentVersion(
        contract_id=contract.id,
        kind="original",
        object_key=key,
        content_hash=content_hash
    )
    contract.head_version_id = v1.id
    await repo_store.save_version(v1)
    await repo_store.save_contract(contract)

    # 2. Start review run
    run = ReviewRun(
        contract_id=contract.id,
        input_version_id=v1.id,
        stance="我方(受托方)"
    )
    await repo_store.save_review_run(run)

    # 3. Execute pipeline
    await run_pipeline_use_case.execute(run.id)

    # 4. Verify review results
    saved_run = await repo_store.get_review_run(run.id)
    assert saved_run.status == ReviewStatus.SUCCEEDED
    assert saved_run.result_version_id is not None

    issues = await repo_store.get_issue_groups(run.id)
    assert len(issues) >= 2  # Found the liability and unilateral termination issues

    plan = await repo_store.get_revision_plan(saved_run.plan_id)
    assert plan is not None
    assert len(plan.operations) >= 2

    # 5. Apply decision (accept first operation)
    first_op = plan.operations[0]
    updated_contract = await repo_store.get_contract(contract.id)

    cmd = await apply_decision_use_case.execute(
        contract_id=contract.id,
        expected_version_id=updated_contract.head_version_id,
        operation_ids=[first_op.id],
        action="accept"
    )
    assert cmd.status == "confirmed"
    assert cmd.confirmed_version_id is not None
    assert cmd.confirmed_version_id != v1.id

    # Verify head advanced
    final_contract = await repo_store.get_contract(contract.id)
    assert final_contract.head_version_id == cmd.confirmed_version_id
    assert final_contract.revision > 1
