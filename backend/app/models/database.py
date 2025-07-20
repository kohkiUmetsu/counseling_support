from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class CounselingSession(Base):
    __tablename__ = "counseling_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_date = Column(DateTime, default=func.now())
    counselor_name = Column(String(100), nullable=False)
    client_age = Column(Integer)
    client_gender = Column(String(10))
    treatment_type = Column(String(100))
    session_duration_minutes = Column(Integer)
    audio_file_path = Column(String(500))
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    transcriptions = relationship("Transcription", back_populates="session")
    improvement_scripts = relationship("ImprovementScript", back_populates="session")

class Transcription(Base):
    __tablename__ = "transcriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("counseling_sessions.id"), nullable=False)
    speaker = Column(String(50))  # counselor, client
    start_time = Column(Float)  # seconds from session start
    end_time = Column(Float)
    text_content = Column(Text, nullable=False)
    confidence_score = Column(Float)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    session = relationship("CounselingSession", back_populates="transcriptions")

class ImprovementScript(Base):
    __tablename__ = "improvement_scripts"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("counseling_sessions.id"), nullable=False)
    original_section = Column(Text, nullable=False)
    improved_section = Column(Text, nullable=False)
    improvement_reason = Column(Text)
    ai_model_used = Column(String(100))
    improvement_score = Column(Float)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    session = relationship("CounselingSession", back_populates="improvement_scripts")

# Vector database model for pgvector
class SuccessConversationVector(Base):
    __tablename__ = "success_conversation_vectors"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_text = Column(Text, nullable=False)
    embedding_vector = Column(Text)  # Will store vector as text, to be replaced with proper vector type
    treatment_category = Column(String(100))
    effectiveness_score = Column(Float)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())