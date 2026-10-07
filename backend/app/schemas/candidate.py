from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

from app.services.resume_parser import ParsedResumeData


class TargetCompanyRequest(BaseModel):
    company_id: str
    company_name: str | None = None
    is_primary: bool = True


class CandidateProfileUpdate(BaseModel):
    branch: str | None = None
    graduation_year: int | None = None
    bio: str | None = None
    target_company: str | None = None


class SelfRatingItem(BaseModel):
    topic_id: str
    rating: float = Field(ge=1.0, le=5.0)


class SelfRatingRequest(BaseModel):
    ratings: list[SelfRatingItem]


class SkillProfileOut(BaseModel):
    topic_id: str
    topic_name: str
    category: str
    self_rating: float
    diagnostic_score: float
    mastery_probability: float
    attempts: int

    class Config:
        from_attributes = True


class CandidateProfileResponse(BaseModel):
    id: str
    user_id: str
    name: str
    email: str
    branch: str | None = None
    graduation_year: int | None = None
    bio: str | None = None
    target_company: str | None = None

    resume_filename: str | None = None
    resume_uploaded_at: datetime | None = None
    resume_signed_url: str | None = None
    parsed_skills: list[str] = []
    parsed_projects: list[dict[str, Any]] = []
    parsed_education: list[dict[str, Any]] = []

    overall_mastery: float = 0.0
    accuracy: float = 0.0
    average_time: float = 0.0
    questions_attempted: int = 0
    questions_solved: int = 0
    current_streak: int = 0

    target_companies: list[dict[str, Any]] = []


class DiagnosticQuestionOut(BaseModel):
    id: str
    topic_id: str
    topic_name: str
    question: str
    options: list[str]

    class Config:
        from_attributes = True


class DiagnosticAnswerItem(BaseModel):
    question_id: str
    selected_index: int


class DiagnosticSubmitRequest(BaseModel):
    answers: list[DiagnosticAnswerItem]


class DiagnosticResultResponse(BaseModel):
    total_questions: int
    correct_count: int
    accuracy_percentage: float
    topic_scores: dict[str, float]
    updated_mastery_profiles: list[SkillProfileOut]


class ResumeUploadResponse(BaseModel):
    message: str
    filename: str
    signed_url: str | None
    parsed: ParsedResumeData
