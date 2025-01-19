import requests
import random
import json
from typing import Dict, List
import time
from faker import Faker

# Initialize Faker for generating random text
fake = Faker()

# Configuration
BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

class TestDataGenerator:
    def __init__(self):
        self.teams: List[Dict] = []
        self.tokens: Dict[str, str] = {}

    def create_team(self, team_name: str, password: str) -> Dict:
        """Create a new team and return the response"""
        url = f"{BASE_URL}/api/teams/register"
        payload = {
            "team_name": team_name,
            "team_full_name": f"Team {team_name.capitalize()}",
            "password": password
        }
        
        try:
            response = requests.post(url, json=payload, headers=HEADERS)
            response.raise_for_status()
            print(f"Created team: {team_name}")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error creating team {team_name}: {str(e)}")
            return None

    def login_team(self, team_name: str, password: str) -> str:
        """Login a team and return the access token"""
        url = f"{BASE_URL}/api/teams/login"
        payload = {
            "team_name": team_name,
            "password": password
        }
        
        try:
            response = requests.post(url, json=payload, headers=HEADERS)
            response.raise_for_status()
            token_data = response.json()
            print(f"Logged in team: {team_name}")
            return token_data["access_token"]
        except requests.exceptions.RequestException as e:
            print(f"Error logging in team {team_name}: {str(e)}")
            return None

    def create_submission(self, team_name: str) -> Dict:
        """Create a random submission for a team"""
        if team_name not in self.tokens:
            print(f"No token found for team {team_name}")
            return None

        url = f"{BASE_URL}/api/submissions"
        headers = {
            **HEADERS,
            "Authorization": f"Bearer {self.tokens[team_name]}"
        }
        
        # Generate random prompt and response
        prompt = fake.text(max_nb_chars=200)
        response = fake.text(max_nb_chars=500)
        
        payload = {
            "prompt": prompt,
            "response": response,
            "table_metadata": {
                "timestamp": str(time.time()),
                "random_seed": random.randint(1, 1000000)
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            print(f"Created submission for team: {team_name}")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error creating submission for team {team_name}: {str(e)}")
            return None

def main():
    generator = TestDataGenerator()
    
    # Create 10 teams
    team_data = [
        ("team_alpha", "password123!"),
        ("team_beta", "password123!"),
        ("team_gamma", "password123!"),
        ("team_delta", "password123!"),
        ("team_epsilon", "password123!"),
        ("team_zeta", "password123!"),
        ("team_eta", "password123!"),
        ("team_theta", "password123!"),
        ("team_iota", "password123!"),
        ("team_kappa", "password123!")
    ]

    # Create teams and store their info
    for team_name, password in team_data:
        team = generator.create_team(team_name, password)
        if team:
            generator.teams.append(team)
            # Login and store token
            token = generator.login_team(team_name, password)
            if token:
                generator.tokens[team_name] = token

    # Create submissions for each team
    for team in generator.teams:
        # Create 2-3 submissions per team
        for _ in range(random.randint(2, 3)):
            generator.create_submission(team["team_name"])
            # Add small delay to avoid overwhelming the server
            time.sleep(0.5)

if __name__ == "__main__":
    main()