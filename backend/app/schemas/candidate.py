from pydantic import BaseModel


class TargetCompanyRequest(BaseModel):
    company_id: str


class CandidateProfileUpdate(BaseModel):
    target_company: str | None = None
    branch: str | None = None
    graduation_year: int | None = None
