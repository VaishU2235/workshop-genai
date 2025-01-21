from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import Optional

def verify_submission_status(status: str):
    if status not in ['verified', 'rejected']:
        raise HTTPException(
            status_code=400,
            detail={
                'error': 'Invalid status',
                'code': 'INVALID_STATUS',
                'details': {
                    'allowed_values': ['verified', 'rejected']
                }
            }
        ) 