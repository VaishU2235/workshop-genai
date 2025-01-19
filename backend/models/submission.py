from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from .base import Base

class Submission(Base):
    __tablename__ = 'submissions'

    submission_id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey('teams.team_id'))
    prompt = Column(String, nullable=False)
    response = Column(String, nullable=False)
    status = Column(String, nullable=False, default='pending')
    table_metadata = Column(JSON, nullable=False, default={})
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())