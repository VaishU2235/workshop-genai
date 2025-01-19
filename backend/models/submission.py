from sqlalchemy import (
    Column, Integer, String, DateTime, JSON, ForeignKey,
    CheckConstraint, text, Index
)
from sqlalchemy.sql import func
from pydantic import BaseModel, Field, Json
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
from .base import Base

class SubmissionStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"

class Submission(Base):
    __tablename__ = 'submissions'

    submission_id = Column(Integer, primary_key=True, index=True)
    team_id = Column(String(20), ForeignKey('teams.team_id'), nullable=False)
    prompt = Column(String, nullable=False)
    response = Column(String, nullable=False)
    match_round = Column(Integer, nullable=False)
    status = Column(
        String(20), 
        nullable=False, 
        default='pending'
    )
    table_metadata = Column(
        JSON, 
        nullable=False, 
        default=lambda: {}
    )
    submitted_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'verified', 'rejected')",
            name='valid_submission_status'
        ),
        CheckConstraint(
            'match_round >= 0',
            name='valid_match_round'
        ),
        # Composite index for quick lookups by team and round
        Index('idx_team_round', team_id, match_round)
    )

# Pydantic models for request/response validation
class SubmissionBase(BaseModel):
    prompt: str = Field(..., min_length=1)
    response: str = Field(..., min_length=1)
    match_round: int = Field(..., ge=0)

class SubmissionCreate(SubmissionBase):
    table_metadata: Dict[str, Any] = Field(default_factory=dict)

class SubmissionUpdate(BaseModel):
    status: SubmissionStatus
    table_metadata: Optional[Dict[str, Any]] = None

class SubmissionRead(SubmissionBase):
    submission_id: int
    team_id: str
    status: SubmissionStatus
    table_metadata: Dict[str, Any]
    submitted_at: datetime

    class Config:
        orm_mode = True

# API Response Models
class SubmissionList(BaseModel):
    items: list[SubmissionRead]
    total: int
    page: int
    size: int

class SubmissionStats(BaseModel):
    total_submissions: int
    submissions_by_round: Dict[int, int]
    submissions_by_status: Dict[str, int]
    team_submission_counts: Dict[str, int]