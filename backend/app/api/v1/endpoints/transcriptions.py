from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.session import CounselingSession
from app.models.transcription import Transcription
from app.services.transcription.whisper_service import whisper_service
from app.services.transcription.speaker_diarization import speaker_diarization_service
from datetime import datetime
import traceback

router = APIRouter()

@router.post("/{session_id}/start")
async def start_transcription(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Start transcription process for a session (synchronous processing)
    """
    # Check if session exists
    session = db.query(CounselingSession).filter(
        CounselingSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check if transcription is already completed
    if session.transcription_status == "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Transcription already {session.transcription_status}"
        )
    
    try:
        # Update session status to processing
        session.transcription_status = "processing"
        db.commit()
        
        # Process transcription directly (synchronous)
        start_time = datetime.utcnow()
        
        # Get audio file from S3 and process
        transcription_result = await whisper_service.transcribe_audio(session_id)
        
        # Perform speaker diarization
        speaker_result = await speaker_diarization_service.process(
            transcription_result["segments"], 
            session_id
        )
        
        # Create transcription record
        transcription = Transcription(
            session_id=session_id,
            full_text=transcription_result["full_text"],
            language=transcription_result["language"],
            duration=transcription_result["duration"],
            segments=speaker_result["segments"],
            speaker_stats=speaker_result["speaker_stats"],
            processing_time=(datetime.utcnow() - start_time).total_seconds(),
            status="completed"
        )
        
        db.add(transcription)
        session.transcription_status = "completed"
        db.commit()
        
        return {
            "message": "Transcription completed",
            "transcription_id": transcription.id,
            "session_id": session_id,
            "status": "completed"
        }
        
    except Exception as e:
        # Handle errors
        session.transcription_status = "failed"
        db.commit()
        
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )

@router.get("/{session_id}/status")
async def get_transcription_status(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get transcription status for a session
    """
    session = db.query(CounselingSession).filter(
        CounselingSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    transcription = db.query(Transcription).filter(
        Transcription.session_id == session_id
    ).first()
    
    response = {
        "session_id": session_id,
        "status": session.transcription_status,
        "transcription_id": transcription.id if transcription else None
    }
    
    if transcription:
        response.update({
            "processing_time": transcription.processing_time,
            "language": transcription.language,
            "duration": transcription.duration,
            "speaker_stats": transcription.speaker_stats
        })
    
    return response

@router.get("/{session_id}")
async def get_transcription(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get transcription data for a session
    """
    session = db.query(CounselingSession).filter(
        CounselingSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    transcription = db.query(Transcription).filter(
        Transcription.session_id == session_id
    ).first()
    
    if not transcription:
        raise HTTPException(status_code=404, detail="Transcription not found")
    
    if transcription.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Transcription not completed. Current status: {transcription.status}"
        )
    
    return {
        "transcription_id": transcription.id,
        "session_id": session_id,
        "full_text": transcription.full_text,
        "language": transcription.language,
        "duration": transcription.duration,
        "segments": transcription.segments,
        "speaker_stats": transcription.speaker_stats,
        "processing_time": transcription.processing_time,
        "created_at": transcription.created_at,
        "updated_at": transcription.updated_at
    }

@router.put("/{transcription_id}/segments/{segment_index}")
async def update_transcription_segment(
    transcription_id: str,
    segment_index: int,
    new_text: str,
    db: Session = Depends(get_db)
):
    """
    Update a specific transcription segment
    """
    transcription = db.query(Transcription).filter(
        Transcription.id == transcription_id
    ).first()
    
    if not transcription:
        raise HTTPException(status_code=404, detail="Transcription not found")
    
    if not transcription.segments or segment_index >= len(transcription.segments):
        raise HTTPException(status_code=404, detail="Segment not found")
    
    # Update the segment
    segments = transcription.segments.copy()
    if "original_text" not in segments[segment_index]:
        segments[segment_index]["original_text"] = segments[segment_index]["text"]
    
    segments[segment_index]["text"] = new_text
    segments[segment_index]["is_edited"] = True
    
    transcription.segments = segments
    db.commit()
    
    return {"message": "Segment updated successfully"}

