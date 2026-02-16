from fastapi import FastAPI
from runtime.coordinator import Coordinator
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

coordinator = Coordinator()

@app.post("/execute")
def execute_workflow(payload: dict):

    print("Received request:", payload)

    result = coordinator.run_execution(
        workflow_id="test_workflow",
        input_payload=payload
    )

    return result
