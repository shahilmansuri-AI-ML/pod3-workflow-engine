CREATE TABLE execution_locks (
    lock_id UUID PRIMARY KEY,
    execution_id UUID REFERENCES executions(execution_id) ON DELETE CASCADE,

    lock_type lock_type NOT NULL,
    locked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE INDEX idx_locks_execution ON execution_locks(execution_id);
