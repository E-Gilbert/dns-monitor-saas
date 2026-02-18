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

    previous_value: Optional[str] = None
    changed: bool = False

    class Config:
        from_attributes = True
