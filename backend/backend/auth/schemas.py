from pydantic import BaseModel, constr, Field

class TeamCreate(BaseModel):
    team_name: constr(min_length=3, max_length=20, pattern="^[a-zA-Z0-9_-]+$")
    team_full_name: constr(min_length=1, max_length=100)
    password: constr(min_length=8, max_length=100)

class TeamLogin(BaseModel):
    team_name: str
    password: str

class TeamResponse(BaseModel):
    team_id: str
    team_name: str
    team_full_name: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    team_id: str
    team_name: str 