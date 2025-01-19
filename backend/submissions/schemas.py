from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Any
from ..models.submission import SubmissionStatus

class SubmissionCreate(BaseModel):
    prompt: str
    response: str
    match_round: int = Field(..., ge=0)
    table_metadata: Dict[str, Any] = Field(default_factory=dict)

class SubmissionUpdate(BaseModel):
    status: SubmissionStatus
    table_metadata: Dict[str, Any] | None = None

class SubmissionResponse(BaseModel):
    submission_id: int
    status: str

class SubmissionDetail(BaseModel):
    submission_id: int
    prompt: str
    response: str
    status: str
    match_round: int
    table_metadata: Dict[str, Any]
    submitted_at: datetime

    class Config:
        from_attributes = True

class AdminSubmissionDetail(SubmissionDetail):
    team_id: str
    team_name: str 