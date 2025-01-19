from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from .base import Base

class Comparison(Base):
    __tablename__ = 'comparisons'
    
    comparison_id = Column(Integer, primary_key=True)
    submission_1_id = Column(Integer, ForeignKey('submissions.submission_id'))
    submission_2_id = Column(Integer, ForeignKey('submissions.submission_id'))
    winner_submission_id = Column(Integer, ForeignKey('submissions.submission_id'))
    loser_submission_id = Column(Integer, ForeignKey('submissions.submission_id'))
    score_difference = Column(Integer)
    comparison_status = Column(
        String(20),
        default='pending'
    )

    # Add constraints as table arguments
    __table_args__ = (
        CheckConstraint("comparison_status IN ('pending', 'completed', 'disputed')", name='valid_status'),
        CheckConstraint('submission_1_id != submission_2_id', name='different_submissions'),
    )

    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime) 