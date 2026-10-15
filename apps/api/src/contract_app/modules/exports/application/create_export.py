import io
from contract_app.infrastructure.persistence.repositories import repo_store
from contract_app.infrastructure.storage.file_storage import file_storage
from contract_app.modules.documents.application.docx_service import docx_service
from contract_app.modules.exports.domain.export_job import ExportJob
from docx import Document

class CreateExportUseCase:
    async def execute(self, contract_id: str, kind: str) -> ExportJob:
        contract = await repo_store.get_contract(contract_id)
        if not contract or not contract.head_version_id:
            raise ValueError(f"Contract {contract_id} head version not found")

        version = await repo_store.get_version(contract.head_version_id)
        if not version:
            raise ValueError(f"Version {contract.head_version_id} not found")

        job = ExportJob(
            contract_id=contract_id,
            source_version_id=version.id,
            kind=kind,
            status="processing"
        )
        await repo_store.save_export_job(job)

        try:
            if kind == "clean_draft":
                # Generate clean draft docx
                run = await repo_store.get_review_run(contract.latest_review_run_id or "")
                plan = await repo_store.get_revision_plan(run.plan_id or "") if run else None
                if plan:
                    art_key, _ = docx_service.apply_revision_plan(version.object_key, plan, clean=True)
                else:
                    raw = file_storage.read_file(version.object_key)
                    art_key, _ = file_storage.save_file(raw, f"clean_{job.id}.docx")
                job.mark_succeeded(art_key, f"{contract.title}_清洁稿.docx")

            elif kind == "track_changes":
                # Track changes draft
                raw = file_storage.read_file(version.object_key)
                art_key, _ = file_storage.save_file(raw, f"track_{job.id}.docx")
                job.mark_succeeded(art_key, f"{contract.title}_带修订稿.docx")

            elif kind == "review_report":
                # Generate review report document
                doc = Document()
                doc.add_heading(f"合同智能审查与复核意见书 - {contract.title}", level=1)
                doc.add_paragraph(f"审查立场: {contract.stance} | 审查版本ID: {version.id}")

                run = await repo_store.get_review_run(contract.latest_review_run_id or "")
                if run:
                    issues = await repo_store.get_issue_groups(run.id)
                    doc.add_heading(f"问题清单与合规意见 (共 {len(issues)} 处条款)", level=2)
                    for ig in issues:
                        doc.add_heading(f"{ig.clause_title} [{ig.severity.upper()}] - 状态: {ig.status}", level=3)
                        doc.add_paragraph(f"【原文事实】: {ig.evidence}")
                        doc.add_paragraph(f"【法律分析】: {ig.public_analysis}")
                        doc.add_paragraph(f"【修改建议】: {ig.proposal}")
                buf = io.BytesIO()
                doc.save(buf)
                art_key, _ = file_storage.save_file(buf.getvalue(), f"report_{job.id}.docx")
                job.mark_succeeded(art_key, f"{contract.title}_审查意见书.docx")

        except Exception as e:
            job.mark_failed(str(e))

        await repo_store.save_export_job(job)
        return job

create_export_use_case = CreateExportUseCase()
