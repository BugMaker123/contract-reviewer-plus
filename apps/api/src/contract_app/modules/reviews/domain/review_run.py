from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional
from contract_app.shared.clock import now_utc
from contract_app.shared.ids import run_id
from contract_app.modules.reviews.domain.review_state import ReviewStatus, PipelineStage

@dataclass
class ReviewRun:
    id: str = field(default_factory=run_id)
    contract_id: str = ""
    input_version_id: str = ""
    stance: str = "我方"
    focus_areas: List[str] = field(default_factory=list)
    condition_hash: str = ""
    status: ReviewStatus = ReviewStatus.QUEUED
    current_stage: PipelineStage = PipelineStage.PREPARE_SNAPSHOT
    deadline: datetime = field(default_factory=lambda: now_utc() + timedelta(seconds=180))
    execution_epoch: int = 1
    lease_owner: Optional[str] = None
    lease_expires_at: Optional[datetime] = None
    attempt: int = 1
    result_version_id: Optional[str] = None
    plan_id: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=now_utc)
    updated_at: datetime = field(default_factory=now_utc)

    def is_cancelled(self) -> bool:
        return self.status in (ReviewStatus.CANCEL_REQUESTED, ReviewStatus.CANCELLED)

    def request_cancel(self):
        if self.status in (ReviewStatus.QUEUED, ReviewStatus.RUNNING):
            self.status = ReviewStatus.CANCEL_REQUESTED
            self.updated_at = now_utc()

    def claim_lease(self, owner: str, lease_seconds: int = 60) -> bool:
        now = now_utc()
        if self.lease_expires_at and self.lease_expires_at > now and self.lease_owner != owner:
            return False
        self.lease_owner = owner
        self.lease_expires_at = now + timedelta(seconds=lease_seconds)
        self.execution_epoch += 1
        self.status = ReviewStatus.RUNNING
        self.updated_at = now
        return True

    def advance_stage(self, stage: PipelineStage):
        self.current_stage = stage
        self.updated_at = now_utc()

    def succeed(self, result_version_id: str, plan_id: str):
        self.status = ReviewStatus.SUCCEEDED
        self.result_version_id = result_version_id
        self.plan_id = plan_id
        self.updated_at = now_utc()

    def fail(self, code: str, message: str):
        self.status = ReviewStatus.FAILED
        self.error_code = code
        self.error_message = message
        self.updated_at = now_utc()
