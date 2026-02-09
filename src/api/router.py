from fastapi import APIRouter
from api.v1.api_v1 import v1_router

general_router = APIRouter()
general_router.include_router(v1_router)
