from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from contract_app.shared.clock import now_utc
from contract_app.shared.ids import export_id

@dataclass
class ExportJob:
    id: str = field(default_factory=export_id)
    contract_id: str = ""
    source_version_id: str = ""
    kind: str = "clean_draft"  # clean_draft, track_changes, review_report
    status: str = "pending"  # pending, processing, succeeded, failed
    artifact_key: Optional[str] = None
    file_name: str = ""
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=now_utc)
    updated_at: datetime = field(default_factory=now_utc)

    def mark_succeeded(self, artifact_key: str, file_name: str):
        self.status = "succeeded"
        self.artifact_key = artifact_key
        self.file_name = file_name
        self.updated_at = now_utc()

    def mark_failed(self, error: str):
        self.status = "failed"
        self.error_message = error
        self.updated_at = now_utc()
