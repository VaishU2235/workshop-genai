# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .auth.router import router as auth_router
from .submissions.router import router as submissions_router
from .matches.router import router as matches_router
from .admin.routes import router as admin_router
from .database import engine
from .models.base import Base
from .utils.scheduler import TaskScheduler
from .tasks.match_tasks import process_matches
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="GenAI Workshop Competition API")
scheduler = TaskScheduler()

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

@app.on_event("startup")
async def startup_event():
    """Initialize and start the scheduler on app startup."""
    try:
        # Schedule match processing task to run every 30 seconds
        scheduler.schedule_interval_task(
            process_matches,
            seconds=30,
            task_id="process_matches_task"
        )
        
        # Start the scheduler
        await scheduler.start()
        
    except Exception as e:
        logging.error(f"Error during startup: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown the scheduler when the app stops."""
    try:
        scheduler.scheduler.shutdown()
        logging.info("Scheduler shut down successfully")
    except Exception as e:
        logging.error(f"Error during shutdown: {e}")
        raise

@app.get("/")
async def root():
    return {"message": "Welcome to GenAI Workshop Competition API"}

