from fastapi import FastAPI
from src.api.router import general_router

middleware = []
app = FastAPI(title="Moderator", middleware=middleware)
app.include_router(general_router)
