from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
import uuid
from app.core.config import settings
from app.schemas.session import SessionUploadResponse, SessionLabelUpdate
from app.services.s3_service import s3_service
from app.db.session import get_db
from app.models.session import CounselingSession

router = APIRouter()

@router.post("/upload", response_model=SessionUploadResponse)
async def upload_audio(
    audio: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Validate file type
    if audio.content_type not in settings.ALLOWED_AUDIO_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(settings.ALLOWED_AUDIO_FORMATS)}"
        )
    
    # Validate file size
    file_size = 0
    contents = await audio.read()
    file_size = len(contents)
    
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
        )
    
    # Reset file pointer
    await audio.seek(0)
    
    # Generate session ID
    session_id = str(uuid.uuid4())
    
    try:
        # Upload to S3
        file_url = s3_service.upload_audio_file(
            file=audio.file,
            file_name=audio.filename,
            content_type=audio.content_type,
            session_id=session_id
        )
        
        # Create database record
        db_session = CounselingSession(
            id=session_id,
            file_url=file_url,
            file_name=audio.filename,
            file_size=file_size,
            file_type=audio.content_type,
            transcription_status="pending"
        )
        db.add(db_session)
        db.commit()
        
        return SessionUploadResponse(
            session_id=session_id,
            file_url=file_url,
            file_name=audio.filename,
            file_size=file_size
        )
        
    except Exception as e:
        # Clean up S3 file if database operation fails
        if 'file_url' in locals():
            s3_service.delete_audio_file(file_url)
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{session_id}/label")
async def update_session_label(
    session_id: str,
    label_data: SessionLabelUpdate,
    db: Session = Depends(get_db)
):
    # Find session
    db_session = db.query(CounselingSession).filter(
        CounselingSession.id == session_id
    ).first()
    
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Update label data
    db_session.is_success = label_data.is_success
    if label_data.counselor_name:
        db_session.counselor_name = label_data.counselor_name
    if label_data.comment:
        db_session.comment = label_data.comment
    
    db.commit()
    db.refresh(db_session)
    
    return db_session

@router.get("/{session_id}")
async def get_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    db_session = db.query(CounselingSession).filter(
        CounselingSession.id == session_id
    ).first()
    
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return db_session

@router.get("/")
async def get_sessions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    sessions = db.query(CounselingSession).offset(skip).limit(limit).all()
    return sessions

@router.get("/{session_id}/audio")
async def get_session_audio(
    session_id: str,
    db: Session = Depends(get_db)
):
    # Find session
    db_session = db.query(CounselingSession).filter(
        CounselingSession.id == session_id
    ).first()
    
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not db_session.file_url:
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    try:
        # Get audio file from S3
        audio_stream = s3_service.get_audio_file_stream(db_session.file_url)
        
        return StreamingResponse(
            audio_stream,
            media_type=db_session.file_type or "audio/mpeg",
            headers={"Content-Disposition": f"inline; filename={db_session.file_name}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve audio file: {str(e)}")