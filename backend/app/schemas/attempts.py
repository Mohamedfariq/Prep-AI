from pydantic import BaseModel, Field


class AttemptCreate(BaseModel):
    question_id: str
    company: str | None = None
    topic: str
    difficulty: str
    correct: bool
    time_taken: float = Field(ge=0)
    attempts: int = Field(default=1, ge=1)
