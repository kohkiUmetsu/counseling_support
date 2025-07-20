from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CounselingSessionBase(BaseModel):
    counselor_name: str
    client_age: Optional[int] = None
    client_gender: Optional[str] = None
    treatment_type: Optional[str] = None
    session_duration_minutes: Optional[int] = None

class CounselingSessionCreate(CounselingSessionBase):
    pass

class CounselingSessionUpdate(BaseModel):
    counselor_name: Optional[str] = None
    client_age: Optional[int] = None
    client_gender: Optional[str] = None
    treatment_type: Optional[str] = None
    session_duration_minutes: Optional[int] = None
    status: Optional[str] = None

class CounselingSessionResponse(CounselingSessionBase):
    id: int
    session_date: datetime
    audio_file_path: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TranscriptionBase(BaseModel):
    speaker: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    text_content: str
    confidence_score: Optional[float] = None

class TranscriptionCreate(TranscriptionBase):
    session_id: int

class TranscriptionResponse(TranscriptionBase):
    id: int
    session_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ImprovementScriptBase(BaseModel):
    original_section: str
    improved_section: str
    improvement_reason: Optional[str] = None
    ai_model_used: Optional[str] = None
    improvement_score: Optional[float] = None

class ImprovementScriptCreate(ImprovementScriptBase):
    session_id: int

class ImprovementScriptResponse(ImprovementScriptBase):
    id: int
    session_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: datetime