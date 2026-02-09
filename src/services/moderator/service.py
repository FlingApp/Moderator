import asyncio
import logging
import warnings
from datetime import datetime

from services.firebase.service import FirebaseService
from utils.firebase import FirebaseManager
from utils.openai_client import client as openai_client
from core.config import config as cfg
from utils.redis_connection import redis_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModeratorService:
    async def get_moderators(self, name_database: str):
        conf = cfg.firebase.__getattribute__(name_database)
        fb_client = await FirebaseManager().get_db(
            name=name_database,
            service_account=conf.model_dump(mode="json"),
        )
        fb_service = FirebaseService(fb_client=fb_client)

        start_time = await redis_service.get("last_moderation_time")
        logger.info(f"last_moderation_time : {start_time}")

        # Get reviews
        reviews_query = await fb_service.get_reviews(
            name_database=name_database,
            start_time=start_time,
            end_time=datetime.now()
        )

        reviews_docs = await reviews_query.get()

        tasks = [self.moderate_item(item=review) for review in reviews_docs]

        results = [r for r in await asyncio.gather(*tasks) if r is not None]

        await fb_service.update_reviews_status_moderator(results)

        await redis_service.set("last_moderation_time", datetime.now().isoformat())
        logger.info("DONE")

    async def moderate_item(self, item) -> dict:
        """
        Moderate a single review
        :return
        idx: str
        flagged: bool
        author_name: str
        text: str
        """
        data = item.to_dict()
        author = data.get("author", {})
        id = data.get("id")
        text = data.get("text")
        bookId = data.get("bookId")

        logger.info(f'Moderating review: {id}, bookId: {bookId}", "authorId": {author.get("id")}')

        # Skip if there is no text
        if not text:
            print(f"Skip idx={id}, empty text")
            return None

        try:
            response = await openai_client.moderations.create(
                model=cfg.openai.model,
                input=str(text),
            )

            return {
                "id": id,
                "flagged": response.results[0].flagged,  # ← only flagged
                "author_id": author.get("id") if isinstance(author, dict) else None,
                "author_name": author.get("name") if isinstance(author, dict) else None,
                "bookId": bookId,
                "text": text.strip(),
            }

        except Exception as e:
            warnings.warn(f"Element {id}: request error: {e}")
            return None


moderator_service = ModeratorService()
