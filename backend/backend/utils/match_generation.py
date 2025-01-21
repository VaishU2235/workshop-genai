import itertools
import logging
from sqlalchemy.orm import Session
from .. import models
from ..admin.routes import CURRENT_ROUND

logger = logging.getLogger(__name__)

def generate_matches_for_team(db: Session, team_id: str) -> int:
    """
    Generate matches for a team against other teams with verified submissions
    Returns number of new matches created
    """
    try:
        # Get all other teams with verified submissions in current round
        other_teams = db.query(models.Team.team_id)\
            .join(models.Submission, models.Team.team_id == models.Submission.team_id)\
            .filter(
                models.Submission.match_round == CURRENT_ROUND,
                models.Submission.status == 'verified',
                models.Team.team_id != team_id
            )\
            .distinct()\
            .all()
        
        other_team_ids = [team[0] for team in other_teams]
        matches_created = 0
        
        # Create matches with each other team
        for other_team_id in other_team_ids:
            # Check if match already exists in either direction
            existing_match = db.query(models.Match)\
                .filter(
                    models.Match.match_round == CURRENT_ROUND,
                    ((models.Match.team1_id == team_id) & (models.Match.team2_id == other_team_id)) |
                    ((models.Match.team1_id == other_team_id) & (models.Match.team2_id == team_id))
                ).first()
            
            if existing_match:
                continue
                
            match = models.Match(
                team1_id=team_id,
                team2_id=other_team_id,
                match_round=CURRENT_ROUND
            )
            db.add(match)
            matches_created += 1
        
        if matches_created > 0:
            db.commit()
            logger.info(f"Created {matches_created} new matches for team {team_id}")
        
        return matches_created
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error generating matches for team {team_id}: {str(e)}")
        return 0 