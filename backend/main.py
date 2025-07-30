from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import create_tables

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # Tables are managed by Alembic migrations
    # create_tables()
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Counseling Support API",
    version="1.0.0",
    description="美容医療クリニック向けカウンセリングスクリプト改善AIツール",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://localhost:3000",
        "https://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

@app.get("/")
async def root():
    return {
        "message": "Counseling Support API",
        "version": "1.0.0",
        "docs": "/docs"
    }