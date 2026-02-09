import logging
from datetime import datetime

from google.cloud import firestore

from utils.firebase import FirebaseManager
from core.config import config as cfg

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FirebaseService:
    def __init__(self, fb_client):
        self.fb_client = fb_client

    async def get_reviews(
        self,
        name_database: str,
        start_time: datetime,
        end_time: datetime,
    ):
        logger.info(f"Time is {start_time} - {end_time}")
        fb_client = await FirebaseManager().get_db(
            name=name_database,
            service_account=cfg.firebase.__getattribute__(name_database),
        )

        all_reviews = fb_client.collection_group("reviews")
        all_reviews = all_reviews \
            .where("date", ">=", start_time) if start_time else all_reviews
        all_reviews = all_reviews \
            .where("date", "<=", end_time) if end_time else all_reviews
        all_reviews = all_reviews.order_by("date", direction=firestore.Query.DESCENDING)

        return all_reviews

    async def update_reviews_status_moderator(self, moderated_reviews: list[dict]):
        logger.info("Updating reviews status")
        logger.info(f"count of reviews: {len(moderated_reviews)}")
        db = self.fb_client

        BATCH_LIMIT = 500
        batch = db.batch()
        counter = 0

        for review in moderated_reviews:
            review_id = review.get("id")
            author_id = review.get("author_id")

            if not review_id or not author_id:
                continue

            ref = (
                db.collection("users")
                .document(author_id)
                .collection("reviews")
                .document(review_id)
            )

            batch.update(ref, {
                "moderatedStatus": "reviewed_ai"
            })

            counter += 1

            if counter % BATCH_LIMIT == 0:
                await batch.commit()
                batch = db.batch()

        if counter % BATCH_LIMIT != 0:
            await batch.commit()
        logger.info("Updated reviews status ;)")
