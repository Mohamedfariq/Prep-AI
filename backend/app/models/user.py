from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.database.postgres import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    graduation_year = Column(Integer, nullable=True)
    branch = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    profile = relationship("CandidateProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    skills = relationship("SkillProfile", back_populates="user", cascade="all, delete-orphan")
    target_companies = relationship("CandidateTargetCompany", back_populates="user", cascade="all, delete-orphan")

    def __getitem__(self, item: str):
        if hasattr(self, item):
            return getattr(self, item)
        raise KeyError(item)

    def get(self, item: str, default=None):
        return getattr(self, item, default)

    def __contains__(self, item: str) -> bool:
        return hasattr(self, item)
