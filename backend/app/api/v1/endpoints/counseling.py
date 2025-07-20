from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_database
from app.models.database import CounselingSession, Transcription, ImprovementScript
from app.schemas.counseling import (
    CounselingSessionCreate,
    CounselingSessionUpdate,
    CounselingSessionResponse,
    TranscriptionCreate,
    TranscriptionResponse,
    ImprovementScriptCreate,
    ImprovementScriptResponse
)

router = APIRouter()

@router.post("/sessions", response_model=CounselingSessionResponse)
def create_counseling_session(
    session_data: CounselingSessionCreate,
    db: Session = Depends(get_database)
):
    """
    Create a new counseling session
    """
    db_session = CounselingSession(**session_data.dict())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

@router.get("/sessions", response_model=List[CounselingSessionResponse])
def get_counseling_sessions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_database)
):
    """
    Get all counseling sessions
    """
    sessions = db.query(CounselingSession).offset(skip).limit(limit).all()
    return sessions

@router.get("/sessions/{session_id}", response_model=CounselingSessionResponse)
def get_counseling_session(
    session_id: int,
    db: Session = Depends(get_database)
):
    """
    Get a specific counseling session
    """
    session = db.query(CounselingSession).filter(CounselingSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.put("/sessions/{session_id}", response_model=CounselingSessionResponse)
def update_counseling_session(
    session_id: int,
    session_update: CounselingSessionUpdate,
    db: Session = Depends(get_database)
):
    """
    Update a counseling session
    """
    session = db.query(CounselingSession).filter(CounselingSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    update_data = session_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(session, field, value)
    
    db.commit()
    db.refresh(session)
    return session

@router.delete("/sessions/{session_id}")
def delete_counseling_session(
    session_id: int,
    db: Session = Depends(get_database)
):
    """
    Delete a counseling session
    """
    session = db.query(CounselingSession).filter(CounselingSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    db.delete(session)
    db.commit()
    return {"message": "Session deleted successfully"}

@router.post("/sessions/{session_id}/transcriptions", response_model=TranscriptionResponse)
def create_transcription(
    session_id: int,
    transcription_data: TranscriptionCreate,
    db: Session = Depends(get_database)
):
    """
    Create a transcription for a session
    """
    # Verify session exists
    session = db.query(CounselingSession).filter(CounselingSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Override session_id from URL
    transcription_data.session_id = session_id
    
    db_transcription = Transcription(**transcription_data.dict())
    db.add(db_transcription)
    db.commit()
    db.refresh(db_transcription)
    return db_transcription

@router.get("/sessions/{session_id}/transcriptions", response_model=List[TranscriptionResponse])
def get_session_transcriptions(
    session_id: int,
    db: Session = Depends(get_database)
):
    """
    Get all transcriptions for a session
    """
    transcriptions = db.query(Transcription).filter(Transcription.session_id == session_id).all()
    return transcriptions

@router.post("/sessions/{session_id}/improvements", response_model=ImprovementScriptResponse)
def create_improvement_script(
    session_id: int,
    improvement_data: ImprovementScriptCreate,
    db: Session = Depends(get_database)
):
    """
    Create an improvement script for a session
    """
    # Verify session exists
    session = db.query(CounselingSession).filter(CounselingSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Override session_id from URL
    improvement_data.session_id = session_id
    
    db_improvement = ImprovementScript(**improvement_data.dict())
    db.add(db_improvement)
    db.commit()
    db.refresh(db_improvement)
    return db_improvement

@router.get("/sessions/{session_id}/improvements", response_model=List[ImprovementScriptResponse])
def get_session_improvements(
    session_id: int,
    db: Session = Depends(get_database)
):
    """
    Get all improvement scripts for a session
    """
    improvements = db.query(ImprovementScript).filter(ImprovementScript.session_id == session_id).all()
    return improvements