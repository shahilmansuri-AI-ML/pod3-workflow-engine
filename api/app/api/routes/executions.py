import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.execution import ExecutionCreate, ExecutionResponse
from app.services.execution_service import ExecutionService

router = APIRouter(prefix="/executions", tags=["executions"])


@router.post("/", response_model=ExecutionResponse)
def create_execution(
    payload: ExecutionCreate,
    db: Session = Depends(get_db),
):
    execution = ExecutionService.create_execution(
        db=db,
        tenant_id=payload.tenant_id,
        agent_id=payload.agent_id,
        trigger_type=payload.trigger_type,
    )

    return execution


@router.get("/{execution_id}", response_model=ExecutionResponse)
def get_execution(
    execution_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    execution = ExecutionService.get_execution(db, execution_id)

    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    return execution
