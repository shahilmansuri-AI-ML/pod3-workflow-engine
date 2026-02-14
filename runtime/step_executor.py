import uuid
import os
import json
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from adapters.adk_adapter import ADKAdapter
from state_manager import StateManager

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class StepExecutor:
    def __init__(self):
        self.adk_adapter = ADKAdapter()
        self.state_manager = StateManager()
    
    def execute_step(self, session, execution_id: uuid.UUID, step_name: str, step_order: int, input_data: dict):
        # Create execution step
        step_id = uuid.uuid4()
        session.execute(
            text("""
            INSERT INTO execution_steps (id, execution_id, step_name, step_order, status, input_payload)
            VALUES (:id, :execution_id, :step_name, :step_order, 'PENDING', :input_payload)
            """),
            {"id": step_id, "execution_id": execution_id, "step_name": step_name, 
             "step_order": step_order, "input_payload": json.dumps(input_data)}
        )
        
        # Write STEP_STARTED event
        self.state_manager.write_event(
            session, execution_id, "STEP_STARTED",
            {"step_name": step_name, "step_order": step_order, "step_id": str(step_id)}
        )
        
        # Update step status to RUNNING
        session.execute(
            text("""
            UPDATE execution_steps 
            SET status = 'RUNNING', started_at = NOW() 
            WHERE id = :id
            """),
            {"id": step_id}
        )
        
        session.commit()
        
        try:
            # Write AGENT_INVOKED event
            self.state_manager.write_event(
                session, execution_id, "AGENT_INVOKED",
                {"agent_name": step_name, "step_id": str(step_id), "input": input_data}
            )
            
            # Invoke ADK agent
            agent_result = self.adk_adapter.invoke_agent(step_name, input_data, {
                "execution_id": str(execution_id),
                "step_id": str(step_id),
                "step_name": step_name
            })
            
            # Write AGENT_RESPONSE event
            self.state_manager.write_event(
                session, execution_id, "AGENT_RESPONSE",
                {"agent_name": step_name, "step_id": str(step_id), "result": agent_result}
            )
            
            # Update step status to SUCCESS
            session.execute(
                text("""
                UPDATE execution_steps 
                SET status = 'SUCCESS', output_payload = :output, completed_at = NOW()
                WHERE id = :id
                """),
                {"id": step_id, "output": json.dumps(agent_result)}
            )
            
            # Write STEP_COMPLETED event
            self.state_manager.write_event(
                session, execution_id, "STEP_COMPLETED",
                {"step_name": step_name, "step_order": step_order, "step_id": str(step_id), "output": agent_result}
            )
            
            session.commit()
            return agent_result
            
        except Exception as e:
            # Update step status to FAILED
            session.execute(
                text("""
                UPDATE execution_steps 
                SET status = 'FAILED', error_message = :error, completed_at = NOW()
                WHERE id = :id
                """),
                {"id": step_id, "error": str(e)}
            )
            
            # Write STEP_FAILED event
            self.state_manager.write_event(
                session, execution_id, "STEP_FAILED",
                {"step_name": step_name, "step_order": step_order, "step_id": str(step_id), "error": str(e)}
            )
            
            session.commit()
            raise e
