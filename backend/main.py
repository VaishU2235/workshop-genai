# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth.router import router as auth_router
from .submissions.router import router as submissions_router
from .admin.routes import router as admin_router  # adjust import path as needed
from .database import engine
from .models.base import Base

# Create database tables
Base.metadata.create_all(bind=engine)

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

@app.get("/")
async def root():
    return {"message": "Welcome to GenAI Workshop Competition API"}

