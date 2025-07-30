from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Main database engine (RDS)
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Vector database engine (Aurora)
vector_engine = create_engine(settings.VECTOR_DATABASE_URL) if settings.VECTOR_DATABASE_URL else engine
VectorSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=vector_engine)

def get_db():
    """Get main database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_vector_db():
    """Get vector database session"""
    db = VectorSessionLocal()
    try:
        yield db
    finally:
        db.close()