from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, 
    CheckConstraint, text, Float
)
from sqlalchemy.sql import func
from pydantic import BaseModel, Field, confloat
from typing import Optional
from datetime import datetime
from enum import Enum
from .base import Base

class ComparisonStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    DISPUTED = "disputed"

class Comparison(Base):
    __tablename__ = 'comparisons'
    
    comparison_id = Column(Integer, primary_key=True)
    submission_1_id = Column(Integer, ForeignKey('submissions.submission_id'), nullable=False)
    submission_2_id = Column(Integer, ForeignKey('submissions.submission_id'), nullable=False)
    winner_submission_id = Column(
        Integer, 
        ForeignKey('submissions.submission_id'),
        nullable=True
    )
    loser_submission_id = Column(
        Integer, 
        ForeignKey('submissions.submission_id'),
        nullable=True
    )
    reviewer_id = Column(String(20), ForeignKey('teams.team_id'), nullable=True)
    reviewer_weightage = Column(Float, nullable=True)
    score_difference = Column(Integer, nullable=True)
    match_round = Column(Integer, nullable=False)
    comparison_status = Column(
        String(20),
        nullable=False,
        default='pending'
    )
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Add constraints as table arguments
    __table_args__ = (
        CheckConstraint("comparison_status IN ('pending', 'completed', 'disputed')", name='valid_status'),
        CheckConstraint('submission_1_id != submission_2_id', name='different_submissions'),
        CheckConstraint('match_round >= 0', name='valid_match_round'),
        CheckConstraint(
            """
            (comparison_status = 'pending' AND winner_submission_id IS NULL 
             AND loser_submission_id IS NULL AND score_difference IS NULL)
            OR 
            (comparison_status IN ('completed', 'disputed') AND winner_submission_id IS NOT NULL 
             AND loser_submission_id IS NOT NULL AND score_difference IS NOT NULL)
            """,
            name='status_dependent_nullability'
        ),
        # Ensure reviewer_weightage is between 0 and 1
        CheckConstraint(
            '(reviewer_weightage IS NULL) OR (reviewer_weightage >= 0 AND reviewer_weightage <= 1)',
            name='valid_reviewer_weightage'
        )
    )

# Pydantic models for request/response validation - Remove from here and define in schemas.py when creating api
class ComparisonBase(BaseModel):
    submission_1_id: int
    submission_2_id: int
    match_round: int = Field(ge=0, description="The round number for this comparison")
    
class ComparisonCreate(ComparisonBase):
    reviewer_id: Optional[str] = None
    reviewer_weightage: Optional[float] = Field(None, ge=0, le=1)

class ComparisonUpdate(BaseModel):
    winner_submission_id: int
    loser_submission_id: int
    score_difference: int
    comparison_status: ComparisonStatus = ComparisonStatus.COMPLETED
    reviewer_weightage: Optional[float] = Field(None, ge=0, le=1)

class ComparisonRead(ComparisonBase):
    comparison_id: int
    winner_submission_id: Optional[int] = None
    loser_submission_id: Optional[int] = None
    reviewer_id: Optional[str] = None
    reviewer_weightage: Optional[float] = None
    score_difference: Optional[int] = None
    comparison_status: ComparisonStatus
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        orm_mode = True