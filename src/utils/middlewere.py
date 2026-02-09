import tempfile
import json
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from apps.sync_bot.src.bot.utils.logger import enable_file_logging, disable_file_logging


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/ai/reviews/moderation/":
            tmp_file = tempfile.NamedTemporaryFile(
                delete=False, suffix=".txt", mode="w+"
            )
            log_file_path = tmp_file.name
            tmp_file.close()

            file_handler = enable_file_logging(log_file_path)
            request.state.log_file_path = log_file_path
            request.state.file_handler = file_handler

            try:
                response = await call_next(request)
            finally:
                disable_file_logging(file_handler)

            if (
                isinstance(response, Response)
                and response.media_type == "application/json"
            ):
                content = json.loads(bytes(response.body).decode("utf-8"))
                content["log_file_path"] = log_file_path
                response = Response(
                    content=json.dumps(content),
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type="application/json",
                )
            return response
        else:
            return await call_next(request)
