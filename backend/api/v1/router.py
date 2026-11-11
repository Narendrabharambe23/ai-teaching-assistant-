"""API v1 router — aggregates all endpoint routers."""
from fastapi import APIRouter
from backend.api.v1.endpoints import documents, chat

api_router = APIRouter()

api_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["Documents"],
)

api_router.include_router(
    chat.router,
    prefix="/chat",
    tags=["Chat"],
)
