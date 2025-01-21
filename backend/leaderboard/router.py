from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from pydantic import BaseModel
from ..database import get_db
from .. import models

router = APIRouter()

class LeaderboardEntry(BaseModel):
    team_id: str
    team_name: str
    score: int  # This will be the elo_score
    wins: int
    losses: int
    rank: int

    class Config:
        orm_mode = True

@router.get("/api/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(db: Session = Depends(get_db)):
    """Get sorted leaderboard with rankings"""
    try:
        # Join leaderboard with teams to get team names
        # Order by elo_score descending
        results = db.query(
            models.Leaderboard,
            models.Team.team_name
        ).join(
            models.Team,
            models.Leaderboard.team_id == models.Team.team_id
        ).order_by(
            desc(models.Leaderboard.elo_score)
        ).all()

        # Convert to response format with rankings
        leaderboard = []
        for rank, (record, team_name) in enumerate(results, start=1):
            leaderboard.append({
                "team_id": record.team_id,
                "team_name": team_name,
                "score": record.elo_score,
                "wins": record.wins,
                "losses": record.losses,
                "rank": rank
            })

        return leaderboard

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 