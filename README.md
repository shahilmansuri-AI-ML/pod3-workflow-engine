# Durable Workflow Execution Runtime

## Quick Start

### Option 1: Docker Compose (Recommended)

1. **Start the services:**
```bash
docker-compose up -d
```

2. **Initialize the database schema:**
```bash
docker-compose exec db psql -U workflow -d workflow -f /docker-entrypoint-initdb.d/schema.sql
```

3. **Run the workflow:**
```bash
docker-compose run --rm runtime
```

4. **Check results:**
```bash
docker-compose exec db psql -U workflow -d workflow -c "SELECT * FROM executions;"
docker-compose exec db psql -U workflow -d workflow -c "SELECT * FROM execution_events ORDER BY timestamp;"
```

### Option 2: Local Development

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Start PostgreSQL:**
```bash
docker run -d --name workflow_db \
  -e POSTGRES_USER=workflow \
  -e POSTGRES_PASSWORD=workflow \
  -e POSTGRES_DB=workflow \
  -p 5432:5432 \
  postgres:15
```

3. **Set up environment:**
```bash
cp .env.example .env
```

4. **Initialize database:**
```bash
psql -h localhost -U workflow -d workflow -f db/schema.sql
```

5. **Run the workflow:**
```bash
python runtime/coordinator.py
```

## Testing the Implementation

### 1. Verify Database Schema
```sql
-- Check all tables exist
\dt

-- Verify table structures
\d executions
\d execution_steps
\d execution_state
\d execution_events
\d execution_locks
```

### 2. Run a Test Execution
```bash
python runtime/coordinator.py
```

Expected output:
```
Execution result: {'status': 'SUCCESS', 'execution_id': 'uuid-here', 'output': {'summarize': {...}, 'extract_entities': {...}}}
```

### 3. Inspect Database State
```sql
-- Check execution record
SELECT id, status, workflow_id, created_at, completed_at FROM executions;

-- Check steps
SELECT step_name, status, retry_count, started_at, completed_at FROM execution_steps;

-- Check events
SELECT event_type, timestamp FROM execution_events ORDER BY timestamp;

-- Check state snapshot
SELECT state_snapshot FROM execution_state;

-- Verify lock is released
SELECT COUNT(*) FROM execution_locks;
```

### 4. Test Concurrency Control
Run multiple instances simultaneously:
```bash
# Terminal 1
python runtime/coordinator.py &

# Terminal 2  
python runtime/coordinator.py &
```

### 5. Test Error Handling
Modify `runtime/coordinator.py` to test failure scenarios:
- Invalid agent name
- Missing input data
- Database connection issues

## Expected Database State After Successful Run

### executions table:
- 1 row with status 'SUCCESS'
- Valid input_payload and output_payload
- Proper timestamps

### execution_steps table:
- 2 rows (summarize, extract_entities)
- Both with status 'SUCCESS'
- Sequential step_order (1, 2)

### execution_state table:
- 1 row with JSON state snapshot
- current_step = 2 (final step)

### execution_events table:
- 7+ events in chronological order:
  - EXECUTION_STARTED
  - STEP_STARTED (x2)
  - AGENT_INVOKED (x2)
  - AGENT_RESPONSE (x2)
  - STEP_COMPLETED (x2)
  - EXECUTION_COMPLETED

### execution_locks table:
- 0 rows (lock released)

## Troubleshooting

### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Test connection
psql -h localhost -U workflow -d workflow -c "SELECT 1;"
```

### Import Errors
```bash
# Verify Python path
python -c "import sys; print(sys.path)"

# Test individual imports
python -c "from runtime.coordinator import Coordinator"
```

### Permission Issues
```bash
# Check file permissions
ls -la runtime/ adapters/ agents/

# Fix if needed
chmod -R 755 runtime/ adapters/ agents/
```

## Monitoring

### Real-time Event Monitoring
```sql
-- Watch events as they happen
SELECT event_type, timestamp, event_payload::text 
FROM execution_events 
ORDER BY timestamp DESC;
```

### Performance Monitoring
```sql
-- Execution duration
SELECT 
  workflow_id,
  status,
  EXTRACT(EPOCH FROM (completed_at - started_at)) as duration_seconds
FROM executions 
WHERE status = 'SUCCESS';
```

## Next Steps

The runtime is ready for:
- Adding more agents to the registry
- Implementing retry logic
- Building DAG execution patterns
- Adding LangGraph/Strand adapters
- Building monitoring dashboards
