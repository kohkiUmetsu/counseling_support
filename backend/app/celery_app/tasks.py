from celery import current_task
from app.celery_app.celery_app import celery_app
from app.services.transcription.whisper_service import whisper_service
from app.services.transcription.speaker_diarization import speaker_diarization_service
from app.websocket.connection_manager import manager
from app.db.session import SessionLocal
from app.models.session import CounselingSession
from app.models.transcription import Transcription
import uuid
import asyncio
from datetime import datetime
import traceback

@celery_app.task(bind=True)
def process_transcription(self, session_id: str):
    """
    Celery task to process audio transcription
    """
    db = SessionLocal()
    start_time = datetime.utcnow()
    
    try:
        # Update task status
        current_task.update_state(
            state="PROCESSING",
            meta={"stage": "initializing", "progress": 0}
        )
        
        # Notify via WebSocket
        try:
            asyncio.create_task(manager.send_progress_update(
                session_id, 0, "initializing", "Starting transcription process"
            ))
        except:
            pass  # WebSocket notification is optional
        
        # Get session from database
        session = db.query(CounselingSession).filter(
            CounselingSession.id == session_id
        ).first()
        
        if not session:
            raise Exception(f"Session {session_id} not found")
        
        # Update session status
        session.transcription_status = "processing"
        db.commit()
        
        # Update task status
        current_task.update_state(
            state="PROCESSING",
            meta={"stage": "downloading_audio", "progress": 10}
        )
        
        # Step 1: Transcribe audio with Whisper
        current_task.update_state(
            state="PROCESSING",
            meta={"stage": "transcribing", "progress": 20}
        )
        
        transcription_result = whisper_service.transcribe_audio(
            audio_file_url=session.file_url,
            session_id=session_id
        )
        
        # Step 2: Speaker diarization
        current_task.update_state(
            state="PROCESSING",
            meta={"stage": "speaker_diarization", "progress": 60}
        )
        
        enhanced_segments = speaker_diarization_service.assign_speakers(
            transcription_result["segments"]
        )
        
        speaker_stats = speaker_diarization_service.get_speaker_statistics(
            enhanced_segments
        )
        
        # Step 3: Save to database
        current_task.update_state(
            state="PROCESSING",
            meta={"stage": "saving_results", "progress": 80}
        )
        
        # Create transcription record
        transcription = Transcription(
            id=str(uuid.uuid4()),
            session_id=session_id,
            full_text=transcription_result["full_text"],
            language=transcription_result["language"],
            duration=transcription_result.get("duration"),
            status="completed",
            segments=enhanced_segments,
            speaker_stats=speaker_stats,
            processing_time=(datetime.utcnow() - start_time).total_seconds()
        )
        
        db.add(transcription)
        
        # Update session
        session.transcription_status = "completed"
        session.duration = transcription_result.get("duration")
        
        db.commit()
        
        # Final update
        current_task.update_state(
            state="SUCCESS",
            meta={
                "stage": "completed",
                "progress": 100,
                "transcription_id": transcription.id,
                "processing_time": transcription.processing_time,
                "speaker_stats": speaker_stats
            }
        )
        
        return {
            "session_id": session_id,
            "transcription_id": transcription.id,
            "status": "completed",
            "processing_time": transcription.processing_time
        }
        
    except Exception as e:
        # Update session status to failed
        try:
            session = db.query(CounselingSession).filter(
                CounselingSession.id == session_id
            ).first()
            if session:
                session.transcription_status = "failed"
                db.commit()
        except:
            pass
        
        # Update task status
        current_task.update_state(
            state="FAILURE",
            meta={
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        )
        
        raise e
        
    finally:
        db.close()

@celery_app.task
def cleanup_old_transcriptions():
    """
    Periodic task to clean up old transcription data
    """
    # Implementation for cleanup (if needed)
    pass