from sqlmodel import create_engine, Session
from dotenv import load_dotenv
import os
from typing import Generator

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Create database engine
engine = create_engine(DATABASE_URL, echo=True)  # echo=True for debug logging

def get_session() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    with Session(engine) as session:
        yield session