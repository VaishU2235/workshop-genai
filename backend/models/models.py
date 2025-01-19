from sqlalchemy import (
    Column, Integer, String, DateTime, Text, 
    BigInteger, ForeignKey, CheckConstraint, JSON
)
from sqlalchemy.sql import func
from .base import Base

class Team(Base):
    __tablename__ = 'teams'
    
    team_id = Column(String(20), primary_key=True)
    team_name = Column(String(20), unique=True, nullable=False)
    team_full_name = Column(String(100))
    team_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    table_metadata = Column(JSON)

class Leaderboard(Base):
    __tablename__ = 'leaderboard'
    
    team_id = Column(String(20), ForeignKey('teams.team_id'), primary_key=True)
    elo_score = Column(BigInteger, default=1000)
    elo_rank = Column(Integer)
    comparisons_made = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    last_match_at = Column(DateTime)
    last_updated = Column(DateTime, server_default=func.now())

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