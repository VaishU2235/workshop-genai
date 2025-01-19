from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class MatchCreate(BaseModel):
    match_round: int = Field(..., ge=0)

class ComparisonSubmit(BaseModel):
    winner_submission_id: int
    loser_submission_id: int
    winner_team_id: str
    loser_team_id: str
    score_difference: int

class MatchResponse(BaseModel):
    comparison_id: int
    submission1: dict
    submission2: dict
    team1_name: str
    team2_name: str 