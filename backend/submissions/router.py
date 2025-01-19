from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List

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
    update: SubmissionUpdate,
    db: Session = Depends(get_db),
    team_id: int = Depends(get_current_team_id)
):
    """Verify or reject a submission"""
    verify_submission_status(update.status)
    
    try:
        submission = db.query(Submission)\
            .filter(
                Submission.submission_id == submission_id,
                Submission.team_id == team_id
            ).first()
            
        if not submission:
            raise HTTPException(
                status_code=404,
                detail={
                    'error': 'Submission not found or access denied',
                    'code': 'NOT_FOUND'
                }
            )
            
        submission.status = update.status
        if update.table_metadata is not None:
            submission.table_metadata = update.table_metadata
        db.commit()
        
        return {
            'submission_id': submission.submission_id,
            'status': submission.status
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