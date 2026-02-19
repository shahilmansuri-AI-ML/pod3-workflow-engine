import json
from sqlalchemy import text
from app.database import SessionLocal
from runtime.lock_manager import LockManager
from runtime.state_manager import StateManager
from runtime.step_executor import StepExecutor


class Coordinator:

    def __init__(self):

        self.lock_manager = LockManager()
        self.state_manager = StateManager()
        self.step_executor = StepExecutor()

    def execute(self, execution_id):

        session = SessionLocal()

        try:

            # Load execution
            execution = session.execute(
                text("""
                SELECT *
                FROM executions
                WHERE execution_id=:execution_id
                """),
                {"execution_id": execution_id}
            ).mappings().first()

            if not execution:
                raise Exception("Execution not found")

            # Load agent metadata
            agent = session.execute(
                text("""
                SELECT *
                FROM agent_registry
                WHERE agent_id=:agent_id
                """),
                {"agent_id": execution["agent_id"]}
            ).mappings().first()

            if not agent:
                raise Exception("Agent not found")

            # Acquire lock
            lock_acquired = self.lock_manager.acquire_execution_lock(
                session,
                execution_id,
                "worker-1"
            )

            if not lock_acquired:
                raise Exception("Execution already locked")

            # Update status RUNNING
            session.execute(
                text("""
                UPDATE executions
                SET status='RUNNING',
                    started_at=NOW()
                WHERE execution_id=:execution_id
                """),
                {"execution_id": execution_id}
            )

            session.commit()

            # Execute step
            result = self.step_executor.execute(
                session,
                execution,
                agent
            )

            # Update execution success
            session.execute(
                text("""
                UPDATE executions
                SET status='COMPLETED',
                    output_payload=:output,
                    completed_at=NOW()
                WHERE execution_id=:execution_id
                """),
                {
                    "execution_id": execution_id,
                    "output": json.dumps(result)
                }
            )

            session.commit()

            return result

        except Exception as e:

            session.execute(
                text("""
                UPDATE executions
                SET status='FAILED',
                    error_message=:error,
                    completed_at=NOW()
                WHERE execution_id=:execution_id
                """),
                {
                    "execution_id": execution_id,
                    "error": str(e)
                }
            )

            session.commit()

            raise e

        finally:

            session.close()
