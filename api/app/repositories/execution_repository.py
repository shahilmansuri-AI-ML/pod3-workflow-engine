import uuid
from sqlalchemy.orm import Session

from app.models.execution import Execution


class ExecutionRepository:

    @staticmethod
    def create_execution(
        db: Session,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        trigger_type: str,
    ) -> Execution:

        execution = Execution(
            execution_id=uuid.uuid4(),
            tenant_id=tenant_id,
            agent_id=agent_id,
            trigger_type=trigger_type,
            status="CREATED",
        )

        db.add(execution)
        db.commit()
        db.refresh(execution)

        return execution

    @staticmethod
    def get_execution(
        db: Session,
        execution_id: uuid.UUID,
    ) -> Execution | None:

        return (
            db.query(Execution)
            .filter(Execution.execution_id == execution_id)
            .first()
        )
