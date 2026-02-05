CREATE TABLE executions (
    execution_id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    agent_id UUID NOT NULL,
    triggered_by_user_id UUID,
    trigger_type trigger_type NOT NULL,
    status execution_status NOT NULL,
    current_step_key VARCHAR,
    parent_execution_id UUID REFERENCES executions(execution_id),

    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_executions_tenant ON executions(tenant_id);
CREATE INDEX idx_executions_status ON executions(status);
