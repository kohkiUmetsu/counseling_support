from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.session import CounselingSession
from app.models.transcription import Transcription
from app.celery_app.tasks import process_transcription
from app.celery_app.celery_app import celery_app

router = APIRouter()

@router.post("/{session_id}/start")
async def start_transcription(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Start transcription process for a session
    """
    # Check if session exists
    session = db.query(CounselingSession).filter(
        CounselingSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check if transcription is already in progress or completed
    if session.transcription_status in ["processing", "completed"]:
        raise HTTPException(
            status_code=400,
            detail=f"Transcription already {session.transcription_status}"
        )
    
    # Start transcription task
    task = process_transcription.delay(session_id)
    
    # Update session status
    session.transcription_status = "processing"
    db.commit()
    
    return {
        "message": "Transcription started",
        "task_id": task.id,
        "session_id": session_id
    }

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

@router.get("/task/{task_id}/status")
async def get_task_status(task_id: str):
    """
    Get Celery task status
    """
    task = celery_app.AsyncResult(task_id)
    
    if task.state == "PENDING":
        response = {
            "task_id": task_id,
            "state": task.state,
            "progress": 0,
            "stage": "waiting"
        }
    elif task.state != "FAILURE":
        response = {
            "task_id": task_id,
            "state": task.state,
            "progress": task.info.get("progress", 0),
            "stage": task.info.get("stage", "unknown")
        }
        if task.state == "SUCCESS":
            response["result"] = task.result
    else:
        response = {
            "task_id": task_id,
            "state": task.state,
            "error": str(task.info.get("error", "Unknown error")),
            "traceback": task.info.get("traceback")
        }
    
    return response