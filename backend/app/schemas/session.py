from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SessionUploadResponse(BaseModel):
    session_id: str = Field(alias="sessionId")
    file_url: str = Field(alias="fileUrl")
    file_name: str = Field(alias="fileName")
    file_size: int = Field(alias="fileSize")
    duration: Optional[float] = None
    
    class Config:
        populate_by_name = True

class SessionLabelUpdate(BaseModel):
    is_success: bool = Field(alias="isSuccess")
    counselor_name: Optional[str] = Field(alias="counselorName")
    comment: Optional[str] = None
    
    class Config:
        populate_by_name = True

class SessionCreate(BaseModel):
    file_url: str
    file_name: str
    file_size: int
    file_type: str
    duration: Optional[float] = None

class Session(BaseModel):
    id: str
    file_url: str
    file_name: str
    file_size: int
    file_type: str
    duration: Optional[float]
    is_success: Optional[bool]
    counselor_name: Optional[str]
    comment: Optional[str]
    transcription_status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True