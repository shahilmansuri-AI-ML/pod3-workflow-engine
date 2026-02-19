CREATE TABLE agent_registry (

    agent_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,

    agent_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- simple prompt-based agent
    system_prompt TEXT NOT NULL,
    model_name VARCHAR(100) NOT NULL,

    status VARCHAR(50) NOT NULL DEFAULT 'DRAFT',

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT unique_agent_per_tenant
        UNIQUE (tenant_id, agent_name)
);
