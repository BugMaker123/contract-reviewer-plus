from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from contract_app.shared.clock import now_utc
from contract_app.shared.ids import contract_id

@dataclass
class Contract:
    id: str = field(default_factory=contract_id)
    title: str = "未命名合同"
    head_version_id: Optional[str] = None
    latest_review_run_id: Optional[str] = None
    revision: int = 1
    stance: str = "我方"  # e.g., 我方(采购方/委托方/提供方)
    review_status: str = "unreviewed"  # unreviewed, reviewing, reviewed, verified
    category_id: Optional[str] = None
    category_name: Optional[str] = None
    checklist_ids: list[str] = field(default_factory=list)
    focus_areas: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=now_utc)
    updated_at: datetime = field(default_factory=now_utc)

    def advance_head(self, new_version_id: str):
        self.head_version_id = new_version_id
        self.revision += 1
        self.updated_at = now_utc()

    def set_review_run(self, run_id: str):
        self.latest_review_run_id = run_id
        self.review_status = "reviewing"
        self.updated_at = now_utc()
