from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class CounselingSession(Base):
    __tablename__ = "counseling_sessions"
    
    id = Column(String(36), primary_key=True)
    file_url = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(50), nullable=False)
    duration = Column(Float, nullable=True)
    
    # Label data
    is_success = Column(Boolean, nullable=True)
    counselor_name = Column(String(255), nullable=True)
    comment = Column(Text, nullable=True)
    
    # Transcription status
    transcription_status = Column(String(20), default="pending")
    # pending, processing, completed, failed
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    transcription = relationship("Transcription", back_populates="session", uselist=False)
    # Note: vectors relationship removed due to database separation