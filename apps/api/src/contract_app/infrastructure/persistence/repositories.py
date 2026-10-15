from typing import Dict, List, Optional
import asyncio
from contract_app.modules.contracts.domain.contract import Contract
from contract_app.modules.documents.domain.version import DocumentVersion
from contract_app.modules.documents.domain.session import EditorSession
from contract_app.modules.reviews.domain.review_run import ReviewRun
from contract_app.modules.issues.domain.issue_group import IssueGroup
from contract_app.modules.revisions.domain.revision_plan import RevisionPlan
from contract_app.modules.revisions.domain.decision_command import DecisionCommand
from contract_app.modules.exports.domain.export_job import ExportJob

class RepositoryStore:
    def __init__(self):
        self.contracts: Dict[str, Contract] = {}
        self.versions: Dict[str, DocumentVersion] = {}
        self.sessions: Dict[str, EditorSession] = {}
        self.review_runs: Dict[str, ReviewRun] = {}
        self.issue_groups: Dict[str, List[IssueGroup]] = {}  # run_id -> list
        self.revision_plans: Dict[str, RevisionPlan] = {}   # plan_id -> plan
        self.decision_commands: Dict[str, DecisionCommand] = {}
        self.export_jobs: Dict[str, ExportJob] = {}
        self._lock = asyncio.Lock()

    # Contracts
    async def save_contract(self, contract: Contract):
        async with self._lock:
            self.contracts[contract.id] = contract

    async def get_contract(self, contract_id: str) -> Optional[Contract]:
        return self.contracts.get(contract_id)

    async def list_contracts(self) -> List[Contract]:
        return sorted(list(self.contracts.values()), key=lambda c: c.updated_at, reverse=True)

    # Versions
    async def save_version(self, version: DocumentVersion):
        async with self._lock:
            self.versions[version.id] = version

    async def get_version(self, version_id: str) -> Optional[DocumentVersion]:
        return self.versions.get(version_id)

    async def list_versions_by_contract(self, contract_id: str) -> List[DocumentVersion]:
        res = [v for v in self.versions.values() if v.contract_id == contract_id]
        return sorted(res, key=lambda v: v.created_at, reverse=True)

    # Sessions
    async def save_session(self, session: EditorSession):
        async with self._lock:
            self.sessions[session.id] = session

    async def get_session(self, session_id: str) -> Optional[EditorSession]:
        return self.sessions.get(session_id)

    # Review Runs
    async def save_review_run(self, run: ReviewRun):
        async with self._lock:
            self.review_runs[run.id] = run

    async def get_review_run(self, run_id: str) -> Optional[ReviewRun]:
        return self.review_runs.get(run_id)

    # Issue Groups
    async def save_issue_groups(self, run_id: str, issues: List[IssueGroup]):
        async with self._lock:
            self.issue_groups[run_id] = issues

    async def get_issue_groups(self, run_id: str) -> List[IssueGroup]:
        return self.issue_groups.get(run_id, [])

    async def get_issue_group(self, run_id: str, issue_id: str) -> Optional[IssueGroup]:
        for ig in self.issue_groups.get(run_id, []):
            if ig.id == issue_id:
                return ig
        return None

    # Revision Plans
    async def save_revision_plan(self, plan: RevisionPlan):
        async with self._lock:
            self.revision_plans[plan.id] = plan

    async def get_revision_plan(self, plan_id: str) -> Optional[RevisionPlan]:
        return self.revision_plans.get(plan_id)

    # Decision Commands
    async def save_decision_command(self, cmd: DecisionCommand):
        async with self._lock:
            self.decision_commands[cmd.id] = cmd

    async def get_decision_command(self, cmd_id: str) -> Optional[DecisionCommand]:
        return self.decision_commands.get(cmd_id)

    # Export Jobs
    async def save_export_job(self, job: ExportJob):
        async with self._lock:
            self.export_jobs[job.id] = job

    async def get_export_job(self, job_id: str) -> Optional[ExportJob]:
        return self.export_jobs.get(job_id)

repo_store = RepositoryStore()
