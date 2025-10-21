# src/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager
from src.config import settings

# Create engine and session factory
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define context manager for DB session
@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db  # provide the session
    finally:
        db.close()  # ensure it's closed, even if error occurs
