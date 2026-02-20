from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from app.database import SessionLocal
from runtime.coordinator import Coordinator
from services.deployment_service import DeploymentService

import json
import uuid
import traceback

app = FastAPI(title="Pod-3 Workflow Execution Engine")

# Coordinator = Orchestration Engine
coordinator = Coordinator()
deployment_service = DeploymentService()


# API 1: REGISTER AGENT
# =====================================================
@app.post("/agents/register")
def register_agent(data: dict):

    session = SessionLocal()

    try:

        # --------------------------
        # Validate required fields
        # --------------------------
        required_fields = [
            "tenant_id",
            "agent_name",
            "system_prompt",
            "model_name",
            "workflow_definition"
        ]

        for field in required_fields:
            if field not in data:
                raise Exception(f"{field} is required")

        # --------------------------
        # Check duplicate agent
        # --------------------------
        existing = session.execute(
            text("""
            SELECT agent_id
            FROM agent_registry
            WHERE tenant_id = :tenant_id
            AND agent_name = :agent_name
            """),
            {
                "tenant_id": data["tenant_id"],
                "agent_name": data["agent_name"]
            }
        ).fetchone()

        if existing:
            raise Exception("Agent already exists for this tenant")

        # --------------------------
        # Insert agent
        # --------------------------
        result = session.execute(
            text("""
            INSERT INTO agent_registry (
                agent_id,
                tenant_id,
                agent_name,
                description,
                agent_type,
                agent_mode,
                execution_framework,
                system_prompt,
                model_name,
                workflow_definition,
                status,
                created_at,
                updated_at
            )
            VALUES (
                gen_random_uuid(),
                :tenant_id,
                :agent_name,
                :description,
                'no_code',
                'single_agent',
                :execution_framework,
                :system_prompt,
                :model_name,
                :workflow_definition,
                'DRAFT',
                NOW(),
                NOW()
            )
            RETURNING agent_id
            """),
                        {
                "tenant_id": data["tenant_id"],
                "agent_name": data["agent_name"],
                "description": data.get("description"),
                "execution_framework": data.get("execution_framework", "ollama"),
                "system_prompt": data["system_prompt"],
                "model_name": data["model_name"],
                "workflow_definition": json.dumps(data["workflow_definition"])
            }
        )

        agent_id = result.scalar()

        session.commit()

        print(f"Agent registered successfully: {agent_id}")

        return {
            "agent_id": str(agent_id),
            "status": "registered"
        }

    except Exception as e:

        session.rollback()

        print("Agent registration failed:", str(e))
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        session.close()


# API 2: DEPLOYE AGENT
# =====================================================     
@app.post("/deployments/deploy-agent")
def deploy_agent(payload: dict):

    agent_id = payload["agent_id"]
    tenant_id = payload["tenant_id"]

    result = deployment_service.deploy_agent(
        agent_id,
        tenant_id
    )

    return result


# API 3: EXECUTE AGENT
# =====================================================
@app.post("/execute/{agent_id}")
def execute(agent_id: str, payload: dict):
    """
    Creates execution and runs orchestration engine.

    WHY this exists:
    - Creates execution record
    - Coordinator handles orchestration
    - Enables resumability and tracking
    """

    session = SessionLocal()

    try:

        print("Execution request received")

        # --------------------------
        # Validate payload
        # --------------------------
        if "tenant_id" not in payload:
            raise Exception("tenant_id is required")

        # --------------------------
        # Validate agent exists
        # --------------------------
        agent = session.execute(
            text("""
            SELECT agent_id
            FROM agent_registry
            WHERE agent_id = :agent_id
            AND status = 'ACTIVE'
            """),
            {"agent_id": agent_id}
        ).fetchone()

        if not agent:
            raise Exception("Agent not found or inactive")

        # --------------------------
        # Insert execution
        # --------------------------
        result = session.execute(
            text("""
            INSERT INTO executions (
                execution_id,
                workflow_id,
                tenant_id,
                agent_id,
                trigger_type,
                status,
                input_payload,
                created_at
            )
            VALUES (
                gen_random_uuid(),
                :workflow_id,
                :tenant_id,
                :agent_id,
                'manual',
                'PENDING',
                :input_payload,
                NOW()
            )
            RETURNING execution_id
            """),
            {
                "workflow_id": "single_agent_workflow",
                "tenant_id": payload["tenant_id"],
                "agent_id": agent_id,
                "input_payload": json.dumps(payload)
            }
        )

        execution_id = result.scalar()

        session.commit()

        print(f"Execution created: {execution_id}")

        # --------------------------
        # Call orchestration engine
        # --------------------------
        result = coordinator.execute(str(execution_id))

        print(f"Execution completed: {execution_id}")

        return {
            "execution_id": str(execution_id),
            "status": "completed",
            "result": result
        }

    except Exception as e:

        session.rollback()

        print("Execution failed:", str(e))
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        session.close()
