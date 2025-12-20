import asyncpg
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    yield
    # Clean up the ML models and release the resources
    ml_models.clear()

app = FastAPI()
