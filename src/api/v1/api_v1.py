from fastapi import APIRouter
from api.v1.ai.controller import router as ai_router

v1_router = APIRouter()
v1_router.include_router(ai_router, prefix="/ai")
