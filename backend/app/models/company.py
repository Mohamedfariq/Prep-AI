from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, DateTime, Integer, JSON, String

from app.database.postgres import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(120), index=True, nullable=False)
    logo = Column(String(50), nullable=True)
    description = Column(String(500), nullable=True)
    tier = Column(String(50), default="Tier-1")
    hiring_stages = Column(JSON, default=list)

    total_questions = Column(Integer, default=0)
    unique_questions = Column(Integer, default=0)
    topic_profile = Column(JSON, default=dict)
    difficulty_profile = Column(JSON, default=dict)
    frequency_profile = Column(JSON, default=dict)
    acceptance_profile = Column(JSON, default=dict)
    recency_profile = Column(JSON, default=dict)
    cluster_profile = Column(JSON, default=dict)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
