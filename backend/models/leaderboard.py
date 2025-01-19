from sqlalchemy import Column, String, DateTime, BigInteger, Integer, ForeignKey
from sqlalchemy.sql import func
from .base import Base

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