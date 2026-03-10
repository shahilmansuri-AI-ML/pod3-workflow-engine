--------------------------------------------------
-- EXTENSIONS
--------------------------------------------------

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

--------------------------------------------------
-- SCHEMA
--------------------------------------------------

CREATE SCHEMA IF NOT EXISTS ai_memory;

--------------------------------------------------
-- DOCUMENT STORAGE
--------------------------------------------------

CREATE TABLE IF NOT EXISTS ai_memory.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    file_name TEXT NOT NULL,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------
-- DOCUMENT CHUNKS (RAG)
--------------------------------------------------

CREATE TABLE IF NOT EXISTS ai_memory.document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES ai_memory.documents(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding VECTOR(1536),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------
-- DOCUMENT EMBEDDINGS
--------------------------------------------------

CREATE TABLE IF NOT EXISTS ai_memory.document_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    document_id UUID,
    chunk TEXT NOT NULL,
    embedding VECTOR(1536),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------
-- SESSION MEMORY
--------------------------------------------------

CREATE TABLE IF NOT EXISTS ai_memory.session_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id UUID,
    tenant_id UUID NOT NULL,
    agent_id UUID NOT NULL,
    role VARCHAR(50),
    content TEXT NOT NULL,
    embedding VECTOR(1536),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------
-- PERSISTENT MEMORY
--------------------------------------------------

CREATE TABLE IF NOT EXISTS ai_memory.persistent_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    agent_id UUID,
    user_id UUID,
    memory_type VARCHAR(50),
    content TEXT NOT NULL,
    embedding VECTOR(1536),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------
-- KNOWLEDGE GRAPH NODES
--------------------------------------------------

CREATE TABLE IF NOT EXISTS ai_memory.knowledge_nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    name TEXT NOT NULL,
    type TEXT,
    embedding VECTOR(1536),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------
-- KNOWLEDGE GRAPH EDGES
--------------------------------------------------

CREATE TABLE IF NOT EXISTS ai_memory.knowledge_edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    source_node_id UUID REFERENCES ai_memory.knowledge_nodes(id) ON DELETE CASCADE,
    target_node_id UUID REFERENCES ai_memory.knowledge_nodes(id) ON DELETE CASCADE,
    relation TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------
-- EMBEDDING JOBS (INGESTION TRACKING)
--------------------------------------------------

CREATE TABLE IF NOT EXISTS ai_memory.embedding_jobs (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    document_id UUID,
    status VARCHAR(50),
    chunks_created INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

--------------------------------------------------
-- VECTOR INDEX METADATA
--------------------------------------------------

CREATE TABLE IF NOT EXISTS ai_memory.vector_index_metadata (
    index_name TEXT PRIMARY KEY,
    table_name TEXT,
    index_type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_rebuilt TIMESTAMP
);

--------------------------------------------------
-- VECTOR INDEXES
--------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_document_chunks_vector
ON ai_memory.document_chunks
USING ivfflat (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_session_memory_vector
ON ai_memory.session_memory
USING ivfflat (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_document_embeddings_vector
ON ai_memory.document_embeddings
USING ivfflat (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_knowledge_nodes_vector
ON ai_memory.knowledge_nodes
USING ivfflat (embedding vector_cosine_ops);

--------------------------------------------------
-- GRAPH TRAVERSAL INDEXES
--------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_graph_source
ON ai_memory.knowledge_edges(source_node_id);

CREATE INDEX IF NOT EXISTS idx_graph_target
ON ai_memory.knowledge_edges(target_node_id);

--------------------------------------------------
-- TENANT FILTER INDEXES
--------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_document_chunks_tenant
ON ai_memory.document_chunks(tenant_id);

CREATE INDEX IF NOT EXISTS idx_session_memory_tenant
ON ai_memory.session_memory(tenant_id);

CREATE INDEX IF NOT EXISTS idx_persistent_memory_tenant
ON ai_memory.persistent_memory(tenant_id);