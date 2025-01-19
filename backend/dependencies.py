from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from .database import get_db
from .auth.utils import SECRET_KEY, ALGORITHM
from .models import Team

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/teams/login")

async def get_current_team(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        team_id: str = payload.get("sub")
        if team_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    team = db.query(Team).filter(Team.team_id == team_id).first()
    if team is None:
        raise credentials_exception
        
    return team 