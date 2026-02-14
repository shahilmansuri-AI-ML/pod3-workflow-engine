import uuid
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class LockManager:
    def acquire_lock(self, session, execution_id: uuid.UUID, worker_id: str, timeout_minutes: int = 30) -> bool:
        expires_at = datetime.utcnow() + timedelta(minutes=timeout_minutes)
        
        try:
            # Try to insert a new lock
            session.execute(
                text("""
                INSERT INTO execution_locks (execution_id, locked_by, expires_at)
                VALUES (:execution_id, :worker_id, :expires_at)
                """),
                {"execution_id": execution_id, "worker_id": worker_id, "expires_at": expires_at}
            )
            return True
        except Exception:
            # Lock already exists, check if it's expired
            result = session.execute(
                text("""
                SELECT locked_by, expires_at FROM execution_locks 
                WHERE execution_id = :execution_id
                """),
                {"execution_id": execution_id}
            ).fetchone()
            
            if not result:
                # Lock was just released, try again
                return self.acquire_lock(session, execution_id, worker_id, timeout_minutes)
            
            locked_by, expires_at = result
            if datetime.utcnow() > expires_at:
                # Lock is expired, remove it and try again
                self.release_lock(session, execution_id)
                return self.acquire_lock(session, execution_id, worker_id, timeout_minutes)
            
            # Lock is held by someone else
            return False
    
    def release_lock(self, session, execution_id: uuid.UUID):
        session.execute(
            text("DELETE FROM execution_locks WHERE execution_id = :execution_id"),
            {"execution_id": execution_id}
        )
    
    def extend_lock(self, session, execution_id: uuid.UUID, worker_id: str, additional_minutes: int = 30) -> bool:
        result = session.execute(
            text("""
            UPDATE execution_locks 
            SET expires_at = :expires_at
            WHERE execution_id = :execution_id AND locked_by = :worker_id
            """),
            {
                "execution_id": execution_id,
                "worker_id": worker_id,
                "expires_at": datetime.utcnow() + timedelta(minutes=additional_minutes)
            }
        )
        
        return result.rowcount > 0
    
    def is_locked(self, session, execution_id: uuid.UUID) -> bool:
        result = session.execute(
            text("""
            SELECT COUNT(*) FROM execution_locks 
            WHERE execution_id = :execution_id AND expires_at > NOW()
            """),
            {"execution_id": execution_id}
        ).fetchone()
        
        return result[0] > 0
    
    def cleanup_expired_locks(self, session):
        session.execute(
            text("DELETE FROM execution_locks WHERE expires_at <= NOW()")
        )
