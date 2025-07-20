from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Transcription(Base):
    __tablename__ = "transcriptions"
    
    id = Column(String(36), primary_key=True)
    session_id = Column(String(36), ForeignKey("counseling_sessions.id"), nullable=False)
    
    # Full transcription text
    full_text = Column(Text, nullable=False)
    
    # Language and metadata
    language = Column(String(10), default="ja")
    duration = Column(Float, nullable=True)
    
    # Processing status
    status = Column(String(20), default="pending")
    # pending, processing, completed, failed
    
    # Segments with timestamps and speaker information
    segments = Column(JSON, nullable=True)
    
    # Speaker statistics
    speaker_stats = Column(JSON, nullable=True)
    
    # Processing metadata
    processing_time = Column(Float, nullable=True)  # seconds
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    session = relationship("CounselingSession", back_populates="transcription")

class TranscriptionSegment(Base):
    __tablename__ = "transcription_segments"
    
    id = Column(String(36), primary_key=True)
    transcription_id = Column(String(36), ForeignKey("transcriptions.id"), nullable=False)
    
    # Segment details
    segment_index = Column(Integer, nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    text = Column(Text, nullable=False)
    
    # Speaker information
    speaker = Column(String(20), nullable=True)  # counselor, client
    speaker_confidence = Column(Float, nullable=True)
    
    # Editing
    is_edited = Column(Boolean, default=False)
    original_text = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    transcription = relationship("Transcription")