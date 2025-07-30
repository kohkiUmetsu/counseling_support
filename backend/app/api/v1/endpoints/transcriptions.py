from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.session import CounselingSession
from app.models.transcription import Transcription
from app.models.vector import SuccessConversationVector
from app.services.transcription.whisper_service import whisper_service
from app.services.transcription.speaker_diarization import speaker_diarization_service
from app.services.embedding_service import embedding_service
from datetime import datetime, timezone
import asyncio
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


async def vectorize_transcription(
    session_id: str,
    full_text: str,  # Kept for potential future use
    segments: list,
    counselor_name: str = None,
    is_success: bool = None
):
    """
    Vectorize transcription and store in vector database
    This runs asynchronously in the background
    """
    vector_db = None
    try:
        # Get vector database session
        from app.db.session import VectorSessionLocal
        vector_db = VectorSessionLocal()
        
        # Check if vectors already exist for this session
        existing_vectors = vector_db.query(SuccessConversationVector).filter(
            SuccessConversationVector.session_id == session_id
        ).first()
        
        if existing_vectors:
            logger.info(f"Vectors already exist for session {session_id}, skipping")
            return
        
        # Prepare conversation text with speaker information
        conversation_chunks = []
        current_chunk = []
        current_tokens = 0
        
        for segment in segments:
            speaker = segment.get("speaker", "unknown")
            text = segment.get("text", "").strip()
            
            if not text:
                continue
                
            # Format: "Speaker: text"
            formatted_segment = f"{speaker}: {text}"
            segment_tokens = embedding_service.count_tokens(formatted_segment)
            
            # Check if adding this segment would exceed max tokens
            if current_tokens + segment_tokens > embedding_service.max_tokens and current_chunk:
                # Save current chunk
                conversation_chunks.append("\n".join(current_chunk))
                current_chunk = [formatted_segment]
                current_tokens = segment_tokens
            else:
                current_chunk.append(formatted_segment)
                current_tokens += segment_tokens
        
        # Add the last chunk
        if current_chunk:
            conversation_chunks.append("\n".join(current_chunk))
        
        # Generate embeddings for each chunk
        logger.info(f"Generating embeddings for {len(conversation_chunks)} chunks from session {session_id}")
        
        for i, chunk_text in enumerate(conversation_chunks):
            try:
                # Generate embedding
                embedding = await embedding_service.embed_text(chunk_text)
                
                # Create vector record
                vector_record = SuccessConversationVector(
                    session_id=session_id,
                    chunk_index=i,
                    chunk_text=chunk_text,
                    embedding=embedding,
                    counselor_name=counselor_name,
                    is_success=is_success if is_success is not None else False,
                    metadata={
                        "chunk_number": i + 1,
                        "total_chunks": len(conversation_chunks),
                        "chunk_tokens": embedding_service.count_tokens(chunk_text)
                    }
                )
                
                vector_db.add(vector_record)
                
            except Exception as chunk_error:
                logger.error(f"Failed to vectorize chunk {i} for session {session_id}: {chunk_error}")
                continue
        
        # Commit all vectors
        vector_db.commit()
        logger.info(f"Successfully vectorized {len(conversation_chunks)} chunks for session {session_id}")
        
    except Exception as e:
        logger.error(f"Vectorization failed for session {session_id}: {str(e)}")
        if vector_db:
            vector_db.rollback()
    finally:
        if vector_db:
            vector_db.close()

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
        start_time = datetime.now(timezone.utc)
        
        # Get audio file from S3 and process
        transcription_result = whisper_service.transcribe_audio(
            session.file_url,
            session_id
        )
        
        # Perform speaker diarization
        try:
            enhanced_segments = speaker_diarization_service.assign_speakers(
                transcription_result["segments"]
            )
            # Calculate speaker statistics
            speaker_stats = speaker_diarization_service.get_speaker_statistics(enhanced_segments)
        except Exception as speaker_error:
            print(f"Speaker diarization error: {speaker_error}")
            print(f"Segments data: {transcription_result['segments']}")
            # Use original segments without speaker assignment
            enhanced_segments = transcription_result["segments"]
            speaker_stats = {}
        
        # Create transcription record
        transcription = Transcription(
            session_id=session_id,
            full_text=transcription_result["full_text"],
            language=transcription_result["language"],
            duration=transcription_result["duration"],
            segments=enhanced_segments,
            speaker_stats=speaker_stats,
            processing_time=(datetime.now(timezone.utc) - start_time).total_seconds(),
            status="completed"
        )
        
        db.add(transcription)
        session.transcription_status = "completed"
        db.commit()
        
        # Automatically vectorize the transcription only for successful sessions
        if session.is_success is True:
            try:
                # Run vectorization in background to avoid blocking the response
                asyncio.create_task(
                    vectorize_transcription(
                        session_id=session_id,
                        full_text=transcription_result["full_text"],
                        segments=enhanced_segments,
                        counselor_name=session.counselor_name,
                        is_success=session.is_success
                    )
                )
                logger.info(f"Started vectorization for successful session {session_id}")
            except Exception as vector_error:
                logger.error(f"Failed to start vectorization for session {session_id}: {vector_error}")
                # Don't fail the transcription if vectorization fails
        else:
            logger.info(f"Skipping vectorization for session {session_id} (is_success={session.is_success})")
        
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

