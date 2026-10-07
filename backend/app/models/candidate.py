from datetime import datetime, timezone
import uuid
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database.postgres import Base


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    bio = Column(String(500), nullable=True)
    target_company = Column(String(100), nullable=True)

    # Resume & Storage Info
    resume_storage_path = Column(String(255), nullable=True)
    resume_filename = Column(String(255), nullable=True)
    resume_uploaded_at = Column(DateTime(timezone=True), nullable=True)
    parsed_skills = Column(JSON, default=list)
    parsed_projects = Column(JSON, default=list)
    parsed_education = Column(JSON, default=list)

    # Performance summary (BKT & practice statistics)
    overall_mastery = Column(Float, default=0.0)
    accuracy = Column(Float, default=0.0)
    average_time = Column(Float, default=0.0)
    questions_attempted = Column(Integer, default=0)
    questions_solved = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="profile")


class SkillProfile(Base):
    __tablename__ = "skill_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(String(100), nullable=False)
    topic_name = Column(String(120), nullable=False)
    category = Column(String(50), nullable=False, default="DSA")  # DSA, CS Fundamentals, Languages

    self_rating = Column(Float, default=2.5)  # 1.0 to 5.0
    diagnostic_score = Column(Float, default=0.0)  # 0.0 to 1.0
    mastery_probability = Column(Float, default=0.25)  # P(L0) seeded via blend: 0.70*diag + 0.30*(self_rating/5)
    attempts = Column(Integer, default=0)

    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="skills")

    __table_args__ = (
        UniqueConstraint("user_id", "topic_id", name="uq_user_topic"),
    )


class CandidateTargetCompany(Base):
    __tablename__ = "candidate_target_companies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    company_id = Column(String(100), nullable=False)
    company_name = Column(String(120), nullable=False)
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="target_companies")

    __table_args__ = (
        UniqueConstraint("user_id", "company_id", name="uq_user_company"),
    )
