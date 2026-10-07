from pydantic import BaseModel


class RecommendationAction(BaseModel):
    note: str | None = None
