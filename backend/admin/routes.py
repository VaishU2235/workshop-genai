from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from .. import models
from .schemas import RoundUpdate
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