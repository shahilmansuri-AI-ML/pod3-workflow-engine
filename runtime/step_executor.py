import uuid
import json
from sqlalchemy import text
from agents.ollama_agent import OllamaAgent


class StepExecutor:

    def __init__(self):

        self.agent = OllamaAgent()

    def execute(self, session, execution, agent_row):

        execution_id = execution["execution_id"]

        step_id = uuid.uuid4()

        session.execute(
            text("""
            INSERT INTO execution_steps (
                step_execution_id,
                execution_id,
                step_name,
                step_key,
                step_order,
                step_type,
                status,
                input_payload
            )
            VALUES (
                :step_id,
                :execution_id,
                'ollama_step',
                'ollama',
                1,
                'llm',
                'RUNNING',
                :input_payload
            )
            """),
            {
                "step_id": step_id,
                "execution_id": execution_id,
                "input_payload": json.dumps(execution["input_payload"])
            }
        )

        result = self.agent.run(
            agent_row["system_prompt"],
            agent_row["model_name"],
            execution["input_payload"]
        )

        session.execute(
            text("""
            UPDATE execution_steps
            SET status='COMPLETED',
                output_payload=:output,
                completed_at=NOW()
            WHERE step_execution_id=:step_id
            """),
            {
                "step_id": step_id,
                "output": json.dumps(result)
            }
        )

        return result
