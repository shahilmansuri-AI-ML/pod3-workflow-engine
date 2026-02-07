import uuid
from sqlalchemy.orm import Session

from app.repositories.execution_repository import ExecutionRepository


class ExecutionService:

    @staticmethod
    def create_execution(
        db: Session,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        trigger_type: str,
    ):
        return ExecutionRepository.create_execution(
            db=db,
            tenant_id=tenant_id,
            agent_id=agent_id,
            trigger_type=trigger_type,
        )

    @staticmethod
    def get_execution(
        db: Session,
        execution_id: uuid.UUID,
    ):
        return ExecutionRepository.get_execution(db, execution_id)
