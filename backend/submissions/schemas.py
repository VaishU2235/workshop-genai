from pydantic import BaseModel
from datetime import datetime

class SubmissionCreate(BaseModel):
    prompt: str
    response: str

class SubmissionUpdate(BaseModel):
    status: str

class SubmissionResponse(BaseModel):
    submission_id: int
    status: str

class SubmissionDetail(BaseModel):
    submission_id: int
    prompt: str
    response: str
    status: str
    submitted_at: datetime

    class Config:
        from_attributes = True

class AdminSubmissionDetail(SubmissionDetail):
    team_id: str
    team_name: str 