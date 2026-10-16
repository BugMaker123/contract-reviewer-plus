from pydantic import BaseModel, Field
from typing import Optional
from contract_app.shared.ids import generate_id
from contract_app.shared.clock import now_iso

class BusinessCategory(BaseModel):
    id: str = Field(default_factory=lambda: generate_id("cat"))
    name: str
    code: str
    description: Optional[str] = ""
    sort_order: int = 1
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)
