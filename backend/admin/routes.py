from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
import itertools
from .. import models
from .schemas import RoundUpdate
from ..matches import schemas
from ..database import get_db
# from ..utils.auth import get_current_admin_user

# Global variable for current round
CURRENT_ROUND = 1

router = APIRouter(prefix="/admin")

@router.get("/round", response_model=Dict[str, int])
async def get_current_round(
    # current_admin: models.Team = Depends(get_current_admin_user)
):
    """Get current match round"""
    return {"current_round": CURRENT_ROUND}

@router.put("/round", response_model=Dict[str, int])
async def update_round(
    round_data: RoundUpdate,
    db: Session = Depends(get_db),
    # current_admin: models.Team = Depends(get_current_admin_user)
):
    """Update current match round"""
    global CURRENT_ROUND
    if round_data.round_number < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Round number cannot be less than 1"
        )
    CURRENT_ROUND = round_data.round_number
    return {"current_round": CURRENT_ROUND}

@router.post("/matches/generate", response_model=dict)
async def generate_matches(
    match_data: schemas.MatchCreate,
    db: Session = Depends(get_db),
    # current_admin: models.Team = Depends(get_current_admin_user)
):
    """Generate all possible team combinations for a round"""
    # Get all teams
    teams = db.query(models.Team).all()
    team_combinations = list(itertools.combinations([team.team_id for team in teams], 2))
    
    matches_created = 0
    for team1_id, team2_id in team_combinations:
        match = models.Match(
            team1_id=team1_id,
            team2_id=team2_id,
            match_round=CURRENT_ROUND
        )
        db.add(match)
        matches_created += 1
        
        # Get latest verified submissions for both teams
        submission1 = db.query(models.Submission)\
            .filter(
                models.Submission.team_id == team1_id,
                models.Submission.status == 'verified',
                models.Submission.match_round == CURRENT_ROUND
            )\
            .order_by(models.Submission.submitted_at.desc())\
            .first()
            
        submission2 = db.query(models.Submission)\
            .filter(
                models.Submission.team_id == team2_id,
                models.Submission.status == 'verified',
                models.Submission.match_round == CURRENT_ROUND
            )\
            .order_by(models.Submission.submitted_at.desc())\
            .first()
            
        if submission1 and submission2:
            comparison = models.Comparison(
                submission_1_id=submission1.submission_id,
                submission_2_id=submission2.submission_id,
                match_round=CURRENT_ROUND,
                comparison_status='pending'
            )
            db.add(comparison)
    
    try:
        db.commit()
        return {"matches_created": matches_created}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 