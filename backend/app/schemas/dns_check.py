from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DNSCheckOut(BaseModel):
    id: int
    domain_id: int
    record_type: str
    resolved_value: Optional[str]
    latency_ms: Optional[int]
    checked_at: datetime
    domain: Optional[str] = None

    # Human-readable "old -> new" description for changed records.
    # For non-changes this may be None.
    change: Optional[str] = None

    # AI-generated explanation of the potential impact of the change.
    # If AI generation fails or is not triggered, this may be None.
    insight: Optional[str] = None

    previous_value: Optional[str] = None
    changed: bool = False

    class Config:
        from_attributes = True
