-- Execution status enums
CREATE TYPE execution_status AS ENUM ('PENDING', 'RUNNING', 'SUCCESS', 'FAILED');
CREATE TYPE step_status AS ENUM ('PENDING', 'RUNNING', 'SUCCESS', 'FAILED');
CREATE TYPE event_type AS ENUM ('EXECUTION_STARTED', 'EXECUTION_COMPLETED', 'EXECUTION_FAILED', 'STEP_STARTED', 'STEP_COMPLETED', 'STEP_FAILED', 'AGENT_INVOKED', 'AGENT_RESPONSE');

-- Main execution table
CREATE TABLE executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id VARCHAR(255) NOT NULL,
    status execution_status NOT NULL DEFAULT 'PENDING',
    input_payload JSONB NOT NULL DEFAULT '{}',
    output_payload JSONB DEFAULT '{}',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Individual execution steps
CREATE TABLE execution_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id UUID NOT NULL REFERENCES executions(id) ON DELETE CASCADE,
    step_name VARCHAR(255) NOT NULL,
    step_order INTEGER NOT NULL,
    status step_status NOT NULL DEFAULT 'PENDING',
    input_payload JSONB NOT NULL DEFAULT '{}',
    output_payload JSONB DEFAULT '{}',
    error_message TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(execution_id, step_order)
);

-- Current execution state for resumability
CREATE TABLE execution_state (
    execution_id UUID PRIMARY KEY REFERENCES executions(id) ON DELETE CASCADE,
    state_snapshot JSONB NOT NULL DEFAULT '{}',
    current_step INTEGER DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Append-only event log for auditability
CREATE TABLE execution_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id UUID NOT NULL REFERENCES executions(id) ON DELETE CASCADE,
    step_id UUID REFERENCES execution_steps(id) ON DELETE SET NULL,
    event_type event_type NOT NULL,
    event_payload JSONB NOT NULL DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Execution locks for concurrency control
CREATE TABLE execution_locks (
    execution_id UUID PRIMARY KEY REFERENCES executions(id) ON DELETE CASCADE,
    locked_by VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_executions_status ON executions(status);
CREATE INDEX idx_executions_workflow_id ON executions(workflow_id);
CREATE INDEX idx_executions_created_at ON executions(created_at);
CREATE INDEX idx_execution_steps_execution_id ON execution_steps(execution_id);
CREATE INDEX idx_execution_steps_status ON execution_steps(status);
CREATE INDEX idx_execution_events_execution_id ON execution_events(execution_id);
CREATE INDEX idx_execution_events_timestamp ON execution_events(timestamp);
CREATE INDEX idx_execution_events_type ON execution_events(event_type);
CREATE INDEX idx_execution_locks_expires_at ON execution_locks(expires_at);

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_executions_updated_at BEFORE UPDATE ON executions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_execution_steps_updated_at BEFORE UPDATE ON execution_steps
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_execution_state_updated_at BEFORE UPDATE ON execution_state
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
