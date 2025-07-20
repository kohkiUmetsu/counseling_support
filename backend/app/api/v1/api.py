from fastapi import APIRouter
from app.api.v1.endpoints import sessions, transcriptions, websocket, vectors, scripts

api_router = APIRouter()

api_router.include_router(
    sessions.router,
    prefix="/sessions",
    tags=["sessions"]
)

api_router.include_router(
    transcriptions.router,
    prefix="/transcriptions",
    tags=["transcriptions"]
)

api_router.include_router(
    websocket.router,
    tags=["websocket"]
)

api_router.include_router(
    vectors.router,
    prefix="/vectors",
    tags=["vectors"]
)

api_router.include_router(
    scripts.router,
    prefix="/scripts",
    tags=["scripts"]
)