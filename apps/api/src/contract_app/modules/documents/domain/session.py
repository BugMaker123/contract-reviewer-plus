from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from contract_app.shared.clock import now_utc
from contract_app.shared.ids import session_id

@dataclass
class EditorSession:
    id: str = field(default_factory=session_id)
    contract_id: str = ""
    base_version_id: str = ""
    provider: str = "onlyoffice"
    document_key: str = ""
    generation: int = 1
    status: str = "active"  # active, closed, saving
    save_checkpoint_id: Optional[str] = None
    created_at: datetime = field(default_factory=now_utc)
    updated_at: datetime = field(default_factory=now_utc)

    def advance_generation(self):
        self.generation += 1
        self.updated_at = now_utc()
