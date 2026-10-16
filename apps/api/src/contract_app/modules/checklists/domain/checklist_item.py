from pydantic import BaseModel, Field
from typing import Optional, Literal
from contract_app.shared.ids import generate_id
from contract_app.shared.clock import now_iso

class ChecklistItem(BaseModel):
    id: str = Field(default_factory=lambda: generate_id("chk"))
    category_id: str
    category_name: Optional[str] = ""
    title: str
    risk_level: Literal["high", "medium", "low"] = "high"
    standard_clause: Optional[str] = ""
    check_prompt: Optional[str] = ""
    prompt_template: Optional[str] = ""
    is_enabled: bool = True
    sort_order: int = 1
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)
