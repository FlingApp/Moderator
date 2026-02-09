import os

from fastapi import APIRouter, Request
from starlette.background import BackgroundTask
from starlette.responses import FileResponse

from api.v1.ai.utils import remove_file
from services.moderator.service import moderator_service


router = APIRouter()


@router.post("/reviews/moderation/")
async def moderation_reviews(request: Request):
    name_database = request.query_params.get("name_database")
    await moderator_service.get_moderators(name_database=name_database)

    log_file_path = getattr(request.state, "log_file_path", None)

    if log_file_path and os.path.exists(log_file_path) and os.path.getsize(log_file_path) > 0:
        return FileResponse(
            path=log_file_path,
            filename=os.path.basename(log_file_path),
            background=BackgroundTask(remove_file, log_file_path)
        )
    return {}

