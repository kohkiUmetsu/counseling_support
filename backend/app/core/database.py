from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.models.database import Base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://counseling_user:counseling_password@localhost:5432/counseling_db")
VECTOR_DATABASE_URL = os.getenv("VECTOR_DATABASE_URL", "postgresql://vector_user:vector_password@localhost:5433/counseling_vector_db")

# Main database engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=True if os.getenv("DEBUG") == "true" else False
)

# Vector database engine
vector_engine = create_engine(
    VECTOR_DATABASE_URL,
    pool_pre_ping=True,
    echo=True if os.getenv("DEBUG") == "true" else False
)

# Session makers
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
VectorSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=vector_engine)

def get_database():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_vector_database():
    """Dependency to get vector database session"""
    db = VectorSessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)
    Base.metadata.create_all(bind=vector_engine)