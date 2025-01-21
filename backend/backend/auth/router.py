from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta

from backend.models.team import Team
from backend.database import get_db
from backend.auth.schemas import TeamCreate, TeamLogin, TeamResponse, Token
from backend.auth.utils import (
    verify_password, get_password_hash, create_access_token,
    generate_team_id, ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/api")

@router.post("/teams/register", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def register_team(team_data: TeamCreate, db: Session = Depends(get_db)):
    # Check if team name already exists
    existing_team = db.query(Team).filter(Team.team_name == team_data.team_name).first()
    if existing_team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team name already registered"
        )
    
    # Create new team
    team_id = generate_team_id()
    hashed_password = get_password_hash(team_data.password)
    
    new_team = Team(
        team_id=team_id,
        team_name=team_data.team_name,
        team_full_name=team_data.team_full_name,
        team_password=hashed_password
    )
    
    try:
        db.add(new_team)
        db.commit()
        db.refresh(new_team)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating team"
        )
    
    return TeamResponse(
        team_id=new_team.team_id,
        team_name=new_team.team_name,
        team_full_name=new_team.team_full_name
    )

@router.post("/teams/login", response_model=Token)
async def login_team(team_credentials: TeamLogin, db: Session = Depends(get_db)):
    # Find team by name
    team = db.query(Team).filter(Team.team_name == team_credentials.team_name).first()
    if not team or not verify_password(team_credentials.password, team.team_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect team name or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": team.team_id, "team_name": team.team_name},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        team_id=team.team_id,
        team_name=team.team_name
    )

# TODO: add admin authentication 
@router.get("/admin/teams", response_model=List[TeamResponse])
async def get_all_teams(db: Session = Depends(get_db)):
    teams = db.query(Team).all()
    return [
        TeamResponse(
            team_id=team.team_id,
            team_name=team.team_name,
            team_full_name=team.team_full_name
        ) for team in teams
    ] 