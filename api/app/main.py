from fastapi import FastAPI
from runtime.coordinator import Coordinator

app = FastAPI()

coordinator = Coordinator()

@app.post("/execute")
def execute_workflow(payload: dict):

    result = coordinator.run_execution(
        workflow_id="test_workflow",
        input_payload=payload
    )

    return result