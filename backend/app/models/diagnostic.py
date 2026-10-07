from sqlalchemy import Column, Integer, JSON, String, Text

from app.database.postgres import Base


class DiagnosticQuestion(Base):
    __tablename__ = "diagnostic_questions"

    id = Column(String(50), primary_key=True)
    topic_id = Column(String(100), index=True, nullable=False)
    topic_name = Column(String(120), nullable=False)
    question = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)  # List of 4 option strings
    correct_index = Column(Integer, nullable=False)
    explanation = Column(Text, nullable=True)
