from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from .. import models
from . import schemas
from ..auth.dependencies import get_current_user
from ..database import get_db

router = APIRouter()

@router.get("/matches/next", response_model=schemas.MatchResponse)
async def get_next_match(
    db: Session = Depends(get_db),
    current_user: models.Team = Depends(get_current_user)
):
    """Get next random match for review"""
    # Get random pending comparison where current user is not involved
    pending_comparison = db.query(models.Comparison)\
        .join(models.Submission, models.Comparison.submission_1_id == models.Submission.submission_id)\
        .filter(
            models.Comparison.comparison_status == 'pending',
            models.Submission.team_id != current_user.team_id,
            models.Comparison.reviewer_id.is_(None)
        )\
        .order_by(func.random())\
        .first()
    
    if not pending_comparison:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pending matches available"
        )
    
    # Get submissions details
    submission1 = db.query(models.Submission).get(pending_comparison.submission_1_id)
    submission2 = db.query(models.Submission).get(pending_comparison.submission_2_id)
    
    # Get team names
    team1 = db.query(models.Team).get(submission1.team_id)
    team2 = db.query(models.Team).get(submission2.team_id)
    
    return {
        "comparison_id": pending_comparison.comparison_id,
        "submission1": {
            "submission_id": submission1.submission_id,
            "prompt": submission1.prompt,
            "response": submission1.response
        },
        "submission2": {
            "submission_id": submission2.submission_id,
            "prompt": submission2.prompt,
            "response": submission2.response
        },
        "team1_name": team1.team_name,
        "team2_name": team2.team_name
    }

@router.post("/comparisons/{comparison_id}/submit")
async def submit_comparison(
    comparison_id: int,
    submission: schemas.ComparisonSubmit,
    db: Session = Depends(get_db),
    current_user: models.Team = Depends(get_current_user)
):
    """Submit comparison results"""
    comparison = db.query(models.Comparison).get(comparison_id)
    if not comparison:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comparison not found"
        )
    
    if comparison.comparison_status != 'pending':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comparison already completed"
        )
    
    # Validate submission IDs match the comparison
    valid_submissions = {comparison.submission_1_id, comparison.submission_2_id}
    if not (submission.winner_submission_id in valid_submissions and 
            submission.loser_submission_id in valid_submissions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid submission IDs"
        )
    
    # Update comparison
    comparison.winner_submission_id = submission.winner_submission_id
    comparison.loser_submission_id = submission.loser_submission_id
    comparison.score_difference = submission.score_difference
    comparison.reviewer_id = current_user.team_id
    comparison.comparison_status = 'completed'
    comparison.completed_at = datetime.utcnow()
    
    try:
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 