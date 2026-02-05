CREATE TABLE execution_state (
    execution_id UUID PRIMARY KEY
        REFERENCES executions(execution_id) ON DELETE CASCADE,

    state_snapshot JSONB NOT NULL,
    last_completed_step_key VARCHAR,
    version INTEGER DEFAULT 1,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
