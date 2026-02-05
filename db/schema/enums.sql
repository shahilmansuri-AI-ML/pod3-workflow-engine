CREATE TYPE execution_status AS ENUM (
    'CREATED',
    'RUNNING',
    'FAILED',
    'COMPLETED',
    'CANCELLED'
);

CREATE TYPE trigger_type AS ENUM (
    'manual',
    'cron',
    'event',
    'agent_call'
);

CREATE TYPE step_status AS ENUM (
    'PENDING',
    'RUNNING',
    'FAILED',
    'COMPLETED'
);

CREATE TYPE step_type AS ENUM (
    'llm',
    'tool',
    'agent_call',
    'condition'
);

CREATE TYPE event_type AS ENUM (
    'EXECUTION_STARTED',
    'STEP_FAILED',
    'RETRY_SCHEDULED',
    'EXECUTION_COMPLETED'
);

CREATE TYPE event_source AS ENUM (
    'executor',
    'orchestrator',
    'agent'
);

CREATE TYPE lock_type AS ENUM (
    'execution',
    'step'
);
