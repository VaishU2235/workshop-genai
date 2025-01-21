from sqlalchemy.orm import Session
from datetime import datetime
from .. import models
import logging

logger = logging.getLogger(__name__)

def sync_teams_to_leaderboard(db: Session) -> None:
    """
    Syncs teams table with leaderboard table.
    Adds missing teams to leaderboard with default values.
    """
    try:
        # Get all team IDs
        team_ids = {team.team_id for team in db.query(models.Team).all()}
        
        # Get existing leaderboard team IDs
        leaderboard_team_ids = {
            record.team_id 
            for record in db.query(models.Leaderboard).all()
        }
        
        # Find teams missing from leaderboard
        missing_team_ids = team_ids - leaderboard_team_ids
        
        # Add missing teams to leaderboard
        for team_id in missing_team_ids:
            new_record = models.Leaderboard(
                team_id=team_id,
                elo_score=1200,
                comparisons_made=0,
                wins=0,
                losses=0,
                last_updated=datetime.utcnow()
            )
            db.add(new_record)
            logger.info(f"Adding team {team_id} to leaderboard with default values")
        
        db.commit()
        
        if missing_team_ids:
            logger.info(f"Added {len(missing_team_ids)} teams to leaderboard")
        else:
            logger.info("No new teams needed to be added to leaderboard")
            
    except Exception as e:
        db.rollback()
        logger.error(f"Error syncing teams to leaderboard: {str(e)}")
        raise 