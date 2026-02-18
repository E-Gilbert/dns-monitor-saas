from pydantic import BaseModel, Field
from datetime import datetime

class DomainCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)

class DomainOut(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True
