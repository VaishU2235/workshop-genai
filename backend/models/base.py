from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

# Configure the engine (you can move this to a config file later)
DATABASE_URL = "postgresql://postgres:nehruworkshop2025@mydbinstance.cpi8oo84o2my.ap-south-1.rds.amazonaws.com:5432/masterdatabase"
engine = create_engine(DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(bind=engine)