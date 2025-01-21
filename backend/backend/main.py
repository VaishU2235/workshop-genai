# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.auth.router import router as auth_router
from backend.submissions.router import router as submissions_router
from backend.matches.router import router as matches_router
from backend.admin.routes import router as admin_router
from backend.leaderboard.router import router as leaderboard_router
from backend.database import engine, SessionLocal
from backend.models.base import Base
from backend.utils.leaderboard_sync import sync_teams_to_leaderboard
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Sync teams to leaderboard
db = SessionLocal()
try:
    sync_teams_to_leaderboard(db)
finally:
    db.close()

app = FastAPI(title="GenAI Workshop Competition API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(submissions_router)
app.include_router(admin_router)
app.include_router(matches_router)
app.include_router(leaderboard_router)

@app.get("/")
async def root():
    return {"message": "Welcome to GenAI Workshop Competition API"}

