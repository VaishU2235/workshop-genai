from pydantic import BaseModel, Field

class RoundUpdate(BaseModel):
    round_number: int = Field(..., ge=1, description="New round number")