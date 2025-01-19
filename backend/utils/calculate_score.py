from typing import Tuple
import math

def calculate_elo_change(
    team1_rating: float,
    team2_rating: float,
    k_factor: float = 32,
    result: float = 1.0  # 1.0 for team1 win, 0.0 for team2 win, 0.5 for draw
) -> Tuple[float, float]:
    """
    Calculate new ELO ratings for two teams based on their match result.
    
    Args:
        team1_rating: Current ELO rating of team 1
        team2_rating: Current ELO rating of team 2
        k_factor: How volatile the ratings are (higher means more movement)
        result: 1.0 if team1 won, 0.0 if team2 won, 0.5 for draw
        
    Returns:
        Tuple containing (new_team1_rating, new_team2_rating)
    """
    # Calculate expected probability of team1 winning
    rating_diff = team2_rating - team1_rating
    expected_team1 = 1 / (1 + math.pow(10, rating_diff / 400))
    expected_team2 = 1 - expected_team1
    
    # Calculate rating changes
    team1_change = k_factor * (result - expected_team1)
    team2_change = k_factor * ((1 - result) - expected_team2)
    
    # Calculate and round new ratings
    new_team1_rating = round(team1_rating + team1_change, 2)
    new_team2_rating = round(team2_rating + team2_change, 2)
    
    return new_team1_rating, new_team2_rating