from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import itertools
from .. import models
from ..matches import schemas
from .deps import get_db, get_current_admin_user

router = APIRouter(prefix="/admin")

@router.post("/matches/generate", response_model=dict)
async def generate_matches(
    match_data: schemas.MatchCreate,
    db: Session = Depends(get_db),
    current_admin: models.Team = Depends(get_current_admin_user)
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
            match_round=match_data.match_round
        )
        db.add(match)
        matches_created += 1
        
        # Get latest verified submissions for both teams
        submission1 = db.query(models.Submission)\
            .filter(
                models.Submission.team_id == team1_id,
                models.Submission.status == 'verified',
                models.Submission.match_round == match_data.match_round
            )\
            .order_by(models.Submission.submitted_at.desc())\
            .first()
            
        submission2 = db.query(models.Submission)\
            .filter(
                models.Submission.team_id == team2_id,
                models.Submission.status == 'verified',
                models.Submission.match_round == match_data.match_round
            )\
            .order_by(models.Submission.submitted_at.desc())\
            .first()
            
        if submission1 and submission2:
            comparison = models.Comparison(
                submission_1_id=submission1.submission_id,
                submission_2_id=submission2.submission_id,
                match_round=match_data.match_round,
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