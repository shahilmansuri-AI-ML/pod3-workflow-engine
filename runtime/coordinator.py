import os
import uuid
import asyncio
import json
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

from runtime.lock_manager import LockManager
from runtime.step_executor import StepExecutor
from runtime.state_manager import StateManager

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class Coordinator:
    def __init__(self):
        self.lock_manager = LockManager()
        self.step_executor = StepExecutor()
        self.state_manager = StateManager()
    
    def run_execution(self, workflow_id: str, input_payload: dict):
        session = SessionLocal()
        execution_id = None
        
        try:
            # Create execution
            execution_id = uuid.uuid4()
            session.execute(
                text("""
                INSERT INTO executions (id, workflow_id, status, input_payload)
                VALUES (:id, :workflow_id, 'PENDING', :input_payload)
                """),
                {"id": execution_id, "workflow_id": workflow_id, "input_payload": json.dumps(input_payload)}
            )
            
            # Write EXECUTION_STARTED event
            self.state_manager.write_event(
                session, execution_id, "EXECUTION_STARTED", 
                {"workflow_id": workflow_id, "input": input_payload}
            )
            
            # Update status to RUNNING
            session.execute(
                text("UPDATE executions SET status = 'RUNNING', started_at = NOW() WHERE id = :id"),
                {"id": execution_id}
            )
            
            session.commit()
            
            # Acquire execution lock
            lock_acquired = self.lock_manager.acquire_lock(session, execution_id, "coordinator")
            if not lock_acquired:
                raise Exception(f"Failed to acquire lock for execution {execution_id}")
            
            session.commit()
            
            # Initialize execution state
            self.state_manager.initialize_state(session, execution_id, {"current_step": 0, "data": input_payload})
            session.commit()
            
            # Execute two agent steps sequentially
            steps = ["ollama"] # "summarize", "extract_entities",
            final_output = {}
            
            for i, step_name in enumerate(steps):
                # Both agents need the original input text, not the accumulated output
                step_input = input_payload
                
                try:
                    # Execute step
                    step_result = self.step_executor.execute_step(
                        session, execution_id, step_name, i + 1, step_input
                    )
                    final_output[step_name] = step_result
                    
                    # Update execution state
                    self.state_manager.update_state(
                        session, execution_id, 
                        {"current_step": i + 1, "data": final_output}
                    )
                    session.commit()
                    
                except Exception as e:
                    # Mark execution as FAILED
                    session.execute(
                        text("""
                        UPDATE executions 
                        SET status = 'FAILED', error_message = :error, completed_at = NOW()
                        WHERE id = :id
                        """),
                        {"id": execution_id, "error": str(e)}
                    )
                    
                    self.state_manager.write_event(
                        session, execution_id, "EXECUTION_FAILED",
                        {"error": str(e), "failed_at_step": step_name}
                    )
                    
                    session.commit()
                    return {"status": "FAILED", "error": str(e)}
            
            # Mark execution as SUCCESS
            session.execute(
                text("""
                UPDATE executions 
                SET status = 'SUCCESS', output_payload = :output, completed_at = NOW()
                WHERE id = :id
                """),
                {"id": execution_id, "output": json.dumps(final_output)}
            )
            
            self.state_manager.write_event(
                session, execution_id, "EXECUTION_COMPLETED",
                {"output": final_output}
            )
            
            session.commit()
            
            return {"status": "SUCCESS", "execution_id": str(execution_id), "output": final_output}
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            # Release lock
            if execution_id:
                try:
                    self.lock_manager.release_lock(session, execution_id)
                    session.commit()
                except:
                    pass
            session.close()

if __name__ == "__main__":
    coordinator = Coordinator()
    result = coordinator.run_execution(
        "test_workflow", 
        {"text": "This is a sample text for testing the workflow execution engine."}
    )
    print(f"Execution result: {result}")
