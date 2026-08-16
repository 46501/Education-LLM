from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from datetime import datetime

class InterviewSetupRequest(BaseModel):
    interview_type: str
    role: str
    experience_level: str
    topics: List[str]
    difficulty: str = "MEDIUM"
    num_questions: int = 5

class InterviewMessageSchema(BaseModel):
    role: str
    content: str
    evaluation: Optional[Dict[str, Any]] = None

class InterviewSessionResponse(BaseModel):
    id: str
    interview_id: str
    status: str
    messages: List[InterviewMessageSchema]

class InterviewAnswerRequest(BaseModel):
    answer: str

class InterviewAnswerResponse(BaseModel):
    evaluation: Dict[str, Any]
    next_question: str

class InterviewResultResponse(BaseModel):
    session_id: str
    score: float
    feedback: Dict[str, Any]
