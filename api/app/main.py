from fastapi import FastAPI
from app.api.router import api_router

app = FastAPI(title="Pod-3 Workflow Engine API")

app.include_router(api_router)
