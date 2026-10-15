from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from contract_app.shared.clock import now_utc
from contract_app.shared.ids import version_id

@dataclass
class DocumentVersion:
    id: str = field(default_factory=version_id)
    contract_id: str = ""
    parent_id: Optional[str] = None
    kind: str = "original"  # original, user_saved, review_baseline, ai_proposal, verified
    object_key: str = ""
    content_hash: str = ""
    created_by: str = "system"
    review_run_id: Optional[str] = None
    created_at: datetime = field(default_factory=now_utc)
    summary: str = ""
    revision_count: int = 0
