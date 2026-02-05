CREATE TABLE execution_steps (
    step_execution_id UUID PRIMARY KEY,
    execution_id UUID REFERENCES executions(execution_id) ON DELETE CASCADE,
    step_key VARCHAR NOT NULL,
    step_type step_type NOT NULL,
    status step_status NOT NULL,

    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,

    input_payload JSONB,
    output_payload JSONB,
    error_message TEXT,

    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_steps_execution ON execution_steps(execution_id);
CREATE INDEX idx_steps_status ON execution_steps(status);
