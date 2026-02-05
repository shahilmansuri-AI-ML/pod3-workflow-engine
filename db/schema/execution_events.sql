CREATE TABLE execution_events (
    event_id UUID PRIMARY KEY,
    execution_id UUID REFERENCES executions(execution_id) ON DELETE CASCADE,

    event_type event_type NOT NULL,
    source event_source NOT NULL,
    payload JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_events_execution ON execution_events(execution_id);
