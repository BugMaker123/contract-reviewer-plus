from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from contract_app.shared.clock import now_utc
from contract_app.shared.ids import operation_id

@dataclass
class RevisionOperation:
    id: str = field(default_factory=operation_id)
    plan_id: str = ""
    issue_group_id: str = ""
    kind: str = "replace"  # insert, delete, replace, comment
    anchor: str = ""
    expected_text: str = ""
    replacement_text: str = ""
    author: str = "法务审查建议"
    public_reason: str = ""
    status: str = "pending"  # pending, accepted, rejected
    created_at: datetime = field(default_factory=now_utc)
    updated_at: datetime = field(default_factory=now_utc)

    def accept(self):
        self.status = "accepted"
        self.updated_at = now_utc()

    def reject(self):
        self.status = "rejected"
        self.updated_at = now_utc()

    def reset(self):
        self.status = "pending"
        self.updated_at = now_utc()
