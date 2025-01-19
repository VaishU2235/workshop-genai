from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
import logging
from .. import models
from . import schemas
from ..auth.dependencies import get_current_team_id
from ..database import get_db
from ..utils.calculate_score import calculate_elo_change

router = APIRouter()

@router.get("/matches/next", response_model=schemas.MatchResponse)
async def get_next_match(
    db: Session = Depends(get_db),
    team_id: models.Team = Depends(get_current_team_id)
):
    """Get next random match for review"""
    # Get random pending comparison where current user is not involved
    pending_comparison = db.query(models.Comparison)\
        .join(models.Submission, models.Comparison.submission_1_id == models.Submission.submission_id)\
        .filter(
            models.Comparison.comparison_status == 'pending',
            models.Submission.team_id != team_id,
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

async def update_team_ratings(db: Session, winner_team_id: int, loser_team_id: int):
    """Update team ratings in the leaderboard after a match"""
    try:
        # Fetch current ratings
        winner_record = db.query(models.Leaderboard).filter(
            models.Leaderboard.team_id == winner_team_id
        ).first()
        loser_record = db.query(models.Leaderboard).filter(
            models.Leaderboard.team_id == loser_team_id
        ).first()
        
        if not winner_record or not loser_record:
            logging.error(f"Leaderboard records not found for teams {winner_team_id}, {loser_team_id}")
            return False
            
        # Calculate new ratings
        new_winner_rating, new_loser_rating = calculate_elo_change(
            team1_rating=winner_record.elo_rating,
            team2_rating=loser_record.elo_rating,
            result=1.0  # Winner is always team1 in this case
        )
        
        # Update ratings
        winner_record.elo_rating = new_winner_rating
        loser_record.elo_rating = new_loser_rating
        
        db.commit()
        
        logging.info(
            f"Updated ratings - Winner Team {winner_team_id}: {new_winner_rating}, "
            f"Loser Team {loser_team_id}: {new_loser_rating}"
        )
        return True
        
    except Exception as e:
        db.rollback()
        logging.error(f"Error updating ratings: {str(e)}")
        return False

def process_ratings_background(db: Session, winner_team_id: int, loser_team_id: int):
    """Background task to process ratings with one retry"""
    success = False
    
    # First attempt
    success = update_team_ratings(db, winner_team_id, loser_team_id)
    
    # Retry once if failed
    if not success:
        logging.info("Retrying rating update...")
        success = update_team_ratings(db, winner_team_id, loser_team_id)
        
    if not success:
        logging.error("Failed to update ratings after retry")

@router.post("/comparisons/{comparison_id}/submit")
async def submit_comparison(
    comparison_id: int,
    submission: schemas.ComparisonSubmit,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    team_id: models.Team = Depends(get_current_team_id)
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
    
    # Validate team IDs match the submissions
    winner_submission = db.query(models.Submission).get(submission.winner_submission_id)
    loser_submission = db.query(models.Submission).get(submission.loser_submission_id)
    
    if not winner_submission or not loser_submission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid submission IDs"
        )
    
    if (winner_submission.team_id != submission.winner_team_id or 
        loser_submission.team_id != submission.loser_team_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team IDs don't match the submissions"
        )
    
    # Update comparison
    comparison.winner_submission_id = submission.winner_submission_id
    comparison.loser_submission_id = submission.loser_submission_id
    comparison.winner_team_id = submission.winner_team_id
    comparison.loser_team_id = submission.loser_team_id
    comparison.score_difference = submission.score_difference
    comparison.reviewer_id = team_id
    comparison.comparison_status = 'completed'
    comparison.completed_at = datetime.utcnow()
    
    try:
        db.commit()
        
        # Add rating update to background tasks
        background_tasks.add_task(
            process_ratings_background,
            db,
            submission.winner_team_id,
            submission.loser_team_id
        )
        
        return {"status": "success"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 