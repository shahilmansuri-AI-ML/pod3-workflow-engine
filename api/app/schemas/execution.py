from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class ExecutionCreate(BaseModel):
    tenant_id: UUID
    agent_id: UUID
    trigger_type: str


class ExecutionResponse(BaseModel):
    execution_id: UUID
    tenant_id: UUID
    agent_id: UUID
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
