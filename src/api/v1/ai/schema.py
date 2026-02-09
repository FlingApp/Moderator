from pydantic import BaseModel


class ModerationReviewsRequest(BaseModel):
    text: str


class ModerationReviewsResponse(BaseModel):
    result: int
