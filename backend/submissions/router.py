from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List
from fastapi import status

from ..database import get_db
from ..models.submission import Submission
from ..models.team import Team
from ..auth import get_current_team_id, require_admin
from .schemas import (
    SubmissionCreate, 
    SubmissionUpdate, 
    SubmissionResponse, 
    SubmissionDetail,
    AdminSubmissionDetail
)
from .dependencies import verify_submission_status
from ..admin.routes import CURRENT_ROUND
from ..utils.match_generation import generate_matches_for_team

router = APIRouter()

@router.post("/api/submissions", response_model=SubmissionResponse, status_code=201)
async def create_submission(
    submission: SubmissionCreate,
    db: Session = Depends(get_db),
    team_id: int = Depends(get_current_team_id)
):
    """Create a new submission"""
    try:
        new_submission = Submission(
            team_id=team_id,
            prompt=submission.prompt,
            response=submission.response,
            match_round=CURRENT_ROUND,
            status='pending',
            table_metadata=submission.table_metadata
        )
        
        db.add(new_submission)
        db.commit()
        db.refresh(new_submission)
        
        return {
            'submission_id': new_submission.submission_id,
            'status': new_submission.status
        }
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                'error': 'Database error',
                'code': 'DB_ERROR',
                'details': str(e)
            }
        )

@router.get("/api/submissions/mine", response_model=List[SubmissionDetail])
async def get_my_submissions(
    db: Session = Depends(get_db),
    team_id: int = Depends(get_current_team_id)
):
    """Get all submissions for the authenticated team"""
    try:
        submissions = db.query(Submission)\
            .filter(Submission.team_id == team_id)\
            .order_by(Submission.submitted_at.desc())\
            .all()
            
        return submissions
        
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail={
                'error': 'Database error',
                'code': 'DB_ERROR',
                'details': str(e)
            }
        )

@router.put("/api/submissions/{submission_id}/verify", response_model=SubmissionResponse)
async def verify_submission(
    submission_id: int,
    submission_update: SubmissionUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    team_id: int = Depends(get_current_team_id)
):
    """Verify or reject a submission"""
    verify_submission_status(submission_update.status)
    
    submission = db.query(Submission)\
        .filter(
            Submission.submission_id == submission_id,
            Submission.team_id == team_id
        ).first()
        
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found or access denied"
        )
    
    # Check if this is the first verified submission for this team in this round
    is_first_verified = False
    if (submission_update.status == 'verified' and 
        submission.status != 'verified'):
        existing_verified = db.query(Submission)\
            .filter(
                Submission.team_id == submission.team_id,
                Submission.match_round == submission.match_round,
                Submission.status == 'verified'
            ).first()
        is_first_verified = not existing_verified
    
    # Update submission
    submission.status = submission_update.status
    if submission_update.table_metadata is not None:
        submission.table_metadata = submission_update.table_metadata
    
    try:
        db.commit()
        
        # If this is team's first verified submission, generate matches
        if is_first_verified:
            background_tasks.add_task(
                generate_matches_for_team,
                db,
                submission.team_id
            )
        
        return {
            'submission_id': submission.submission_id,
            'status': submission.status
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/api/admin/submissions", response_model=List[AdminSubmissionDetail])
async def list_submissions(
    status: Optional[str] = None,
    team_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin)
):
    """List all submissions (admin only)"""
    try:
        query = db.query(Submission, Team)\
            .join(Team, Submission.team_id == Team.team_id)
        
        if status:
            query = query.filter(Submission.status == status)
            
        if team_id:
            query = query.filter(Submission.team_id == team_id)
            
        results = query.order_by(Submission.submitted_at.desc()).all()
        
        return [{
            'submission_id': sub.submission_id,
            'team_id': sub.team_id,
            'team_name': team.team_name,
            'prompt': sub.prompt,
            'response': sub.response,
            'status': sub.status,
            'match_round': sub.match_round,
            'table_metadata': sub.table_metadata,
            'submitted_at': sub.submitted_at
        } for sub, team in results]
        
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail={
                'error': 'Database error',
                'code': 'DB_ERROR',
                'details': str(e)
            }
        ) 