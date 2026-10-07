from pydantic import BaseModel, Field


class AssessmentStartRequest(BaseModel):
    company_id: str | None = None
    question_count: int = Field(default=5, ge=1, le=20)
    duration_minutes: int = Field(default=45, ge=10, le=180)


class AssessmentSubmitRequest(BaseModel):
    answers: list[dict]
