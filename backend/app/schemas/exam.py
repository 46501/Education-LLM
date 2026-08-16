from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from datetime import datetime

class ExamTopicSchema(BaseModel):
    topic_id: str
    weight: float = 1.0
    priority: str = "MEDIUM"

class ExamCreate(BaseModel):
    title: str
    description: Optional[str] = None
    exam_date: Optional[datetime] = None
    duration_minutes: int = 60
    total_marks: float = 100.0
    topics: List[ExamTopicSchema]

class ExamQuestionSchema(BaseModel):
    question_id: str
    question_text: str
    question_type: str
    difficulty: str
    options: Optional[Any] = None
    marks: float
    question_order: int

class ExamSessionResponse(BaseModel):
    id: str
    exam_id: str
    started_at: datetime
    duration_minutes: int
    status: str
    questions: List[ExamQuestionSchema]

class AnswerSubmission(BaseModel):
    question_id: str
    answer: Any

class ExamSubmitRequest(BaseModel):
    answers: List[AnswerSubmission]

class ExamResultResponse(BaseModel):
    exam_session_id: str
    score: float
    total_marks: float
    percentage: float
    topic_analysis: List[Dict[str, Any]]
    difficulty_analysis: Dict[str, Any]
    mistakes: List[Dict[str, Any]]
    recommendations: List[str]
