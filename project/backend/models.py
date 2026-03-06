from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class SessionStatus(str, Enum):
    in_progress = "in_progress"
    completed = "completed"
    abandoned = "abandoned"

class InputMode(str, Enum):
    text = "text"
    audio = "audio"
    video = "video"

# Request Models
class CreateSessionRequest(BaseModel):
    resume_text: Optional[str] = None
    resume_filename: Optional[str] = None
    personality: str
    user_id: Optional[str] = None

class UpdateStatusRequest(BaseModel):
    status: SessionStatus

class ResponseData(BaseModel):
    question_index: int
    question: str
    answer: str
    input_mode: InputMode = InputMode.text
    recording_duration: int = 0
    timestamp: int

class SaveResponseRequest(BaseModel):
    session_id: str
    question_index: int
    question: str
    answer: str
    input_mode: InputMode = InputMode.text
    recording_duration: int = 0
    timestamp: int

class BatchResponsesRequest(BaseModel):
    session_id: str
    responses: List[ResponseData]

class SaveResultsRequest(BaseModel):
    session_id: str
    technical_accuracy: float
    language_proficiency: float
    confidence_level: float
    sentiment_score: float
    emotional_stability: float
    feedback: Optional[str] = None

# Response Models
class SessionResponse(BaseModel):
    id: str
    user_id: Optional[str]
    resume_text: Optional[str]
    resume_filename: Optional[str]
    personality: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime]

class InterviewResponseModel(BaseModel):
    id: str
    session_id: str
    question_index: int
    question: str
    answer: str
    input_mode: str
    recording_duration: int
    timestamp: int

class PerformanceResultModel(BaseModel):
    id: str
    session_id: str
    technical_accuracy: float
    language_proficiency: float
    confidence_level: float
    sentiment_score: float
    emotional_stability: float
    overall_score: float
    feedback: Optional[str]

class ApiResponse(BaseModel):
    success: bool
    data: Optional[dict | list] = None
    error: Optional[str] = None
    message: Optional[str] = None
