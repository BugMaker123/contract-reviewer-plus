from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from contract_app.shared.clock import now_utc
from contract_app.shared.ids import plan_id
from contract_app.modules.revisions.domain.operation import RevisionOperation

@dataclass
class RevisionPlan:
    id: str = field(default_factory=plan_id)
    review_run_id: str = ""
    base_version_id: str = ""
    operations: List[RevisionOperation] = field(default_factory=list)
    created_at: datetime = field(default_factory=now_utc)
    updated_at: datetime = field(default_factory=now_utc)

    def get_operation(self, op_id: str):
        for op in self.operations:
            if op.id == op_id:
                return op
        return None
