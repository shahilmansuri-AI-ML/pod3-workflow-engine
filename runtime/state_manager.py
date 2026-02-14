import uuid
import json
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class StateManager:
    def initialize_state(self, session, execution_id: uuid.UUID, initial_state: dict):
        session.execute(
            text("""
            INSERT INTO execution_state (execution_id, state_snapshot, current_step)
            VALUES (:execution_id, :state_snapshot, :current_step)
            ON CONFLICT (execution_id) DO UPDATE SET
                state_snapshot = EXCLUDED.state_snapshot,
                current_step = EXCLUDED.current_step,
                updated_at = NOW()
            """),
            {"execution_id": execution_id, "state_snapshot": json.dumps(initial_state), "current_step": 0}
        )
    
    def update_state(self, session, execution_id: uuid.UUID, state: dict):
        session.execute(
            text("""
            UPDATE execution_state 
            SET state_snapshot = :state_snapshot, updated_at = NOW()
            WHERE execution_id = :execution_id
            """),
            {"execution_id": execution_id, "state_snapshot": json.dumps(state)}
        )
    
    def get_state(self, session, execution_id: uuid.UUID) -> dict:
        result = session.execute(
            text("SELECT state_snapshot FROM execution_state WHERE execution_id = :execution_id"),
            {"execution_id": execution_id}
        ).fetchone()
        
        if result:
            return json.loads(result[0]) if result[0] else {}
        return {}
    
    def write_event(self, session, execution_id: uuid.UUID, event_type: str, payload: dict, step_id: uuid.UUID = None):
        session.execute(
            text("""
            INSERT INTO execution_events (execution_id, step_id, event_type, event_payload)
            VALUES (:execution_id, :step_id, :event_type, :event_payload)
            """),
            {
                "execution_id": execution_id,
                "step_id": step_id,
                "event_type": event_type,
                "event_payload": json.dumps(payload)
            }
        )
    
    def get_events(self, session, execution_id: uuid.UUID) -> list:
        result = session.execute(
            text("""
            SELECT event_type, event_payload, timestamp, step_id
            FROM execution_events 
            WHERE execution_id = :execution_id 
            ORDER BY timestamp ASC
            """),
            {"execution_id": execution_id}
        ).fetchall()
        
        events = []
        for row in result:
            events.append({
                "event_type": row[0],
                "event_payload": json.loads(row[1]) if row[1] else {},
                "timestamp": row[2].isoformat() if row[2] else None,
                "step_id": str(row[3]) if row[3] else None
            })
        return events
