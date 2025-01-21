# models/match.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.sql import func
from backend.models.base import Base

class Match(Base):
    __tablename__ = 'matches'
    
    match_id = Column(Integer, primary_key=True)
    team1_id = Column(String(20), ForeignKey('teams.team_id'), nullable=False)
    team2_id = Column(String(20), ForeignKey('teams.team_id'), nullable=False)
    match_round = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    __table_args__ = (
        CheckConstraint('team1_id != team2_id', name='different_teams'),
        CheckConstraint('match_round >= 0', name='valid_match_round'),
        UniqueConstraint('team1_id', 'team2_id', 'match_round', name='unique_match_combination')
    )