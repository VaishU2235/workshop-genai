from sqlalchemy import Column, String, DateTime, JSON
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