from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    graduation_year: int = Field(ge=2024, le=2035)
    branch: str = Field(min_length=2, max_length=80)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember: bool = False


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict
