from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from contract_app.shared.clock import now_utc
from contract_app.shared.ids import command_id

@dataclass
class DecisionCommand:
    id: str = field(default_factory=command_id)
    contract_id: str = ""
    expected_version_id: str = ""
    operation_ids: List[str] = field(default_factory=list)
    action: str = "accept"  # accept, reject, reset
    status: str = "requested"  # requested, executing, awaiting_save, confirmed, failed
    confirmed_version_id: Optional[str] = None
    error_message: Optional[str] = None
    idempotency_key: Optional[str] = None
    created_at: datetime = field(default_factory=now_utc)
    updated_at: datetime = field(default_factory=now_utc)

    def mark_executing(self):
        self.status = "executing"
        self.updated_at = now_utc()

    def mark_awaiting_save(self):
        self.status = "awaiting_save"
        self.updated_at = now_utc()

    def mark_confirmed(self, confirmed_version_id: str):
        self.status = "confirmed"
        self.confirmed_version_id = confirmed_version_id
        self.updated_at = now_utc()

    def mark_failed(self, error: str):
        self.status = "failed"
        self.error_message = error
        self.updated_at = now_utc()
