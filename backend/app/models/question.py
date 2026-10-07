from datetime import datetime, timezone
import uuid
from sqlalchemy import Boolean, Column, DateTime, Float, Index, Integer, JSON, String

from app.database.postgres import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    question_id = Column(String(255), unique=True, index=True, nullable=False)
    question_key = Column(String(255), index=True, nullable=False)
    title = Column(String(500), index=True, nullable=False)
    leetcode_url = Column(String(1000), nullable=True)
    difficulty = Column(String(100), index=True, nullable=False)
    topics = Column(JSON, default=list)  # List of topic strings
    frequency_percent = Column(Float, default=0.0)
    acceptance_rate_percent = Column(Float, default=0.0)
    companies = Column(JSON, default=list)  # List of company IDs/slugs

    recency_buckets = Column(String(255), nullable=True)
    has_thirty_days = Column(Boolean, default=False)
    has_three_months = Column(Boolean, default=False)
    has_six_months = Column(Boolean, default=False)
    has_more_than_six_months = Column(Boolean, default=False)
    has_all = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
