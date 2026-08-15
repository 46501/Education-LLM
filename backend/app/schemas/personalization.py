from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class LearningProfileBase(BaseModel):
    current_streak: int
    longest_streak: int
    last_active_date: Optional[datetime] = None

class LearningProfileResponse(LearningProfileBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LearningPreferenceUpdate(BaseModel):
    explanation_style: Optional[str] = None
    practice_preference: Optional[str] = None
    difficulty_preference: Optional[str] = None

class LearningPreferenceResponse(BaseModel):
    id: str
    user_id: str
    explanation_style: str
    practice_preference: str
    difficulty_preference: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LearningMemoryCreate(BaseModel):
    memory_type: str
    topic_id: Optional[str] = None
    content: str
    confidence: float
    source: Optional[str] = None

class LearningMemoryResponse(LearningMemoryCreate):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class StudyPlanItemBase(BaseModel):
    topic_id: Optional[str] = None
    activity_type: str
    estimated_minutes: int
    priority: str
    scheduled_date: Optional[datetime] = None
    status: str

class StudyPlanItemResponse(StudyPlanItemBase):
    id: str
    plan_id: str
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class StudyPlanBase(BaseModel):
    title: str
    goal: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: str

class StudyPlanResponse(StudyPlanBase):
    id: str
    user_id: str
    items: List[StudyPlanItemResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class StudyPlanGenerateRequest(BaseModel):
    goal: str
    duration_days: int = 1
    available_minutes_per_day: int = 60

class RevisionScheduleResponse(BaseModel):
    id: str
    user_id: str
    topic_id: str
    last_reviewed: Optional[datetime] = None
    next_review: datetime
    interval_days: float
    review_count: int
    ease_score: float
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TopicPrerequisiteResponse(BaseModel):
    id: str
    topic_id: str
    prerequisite_topic_id: str

    class Config:
        from_attributes = True

class StudySessionCreate(BaseModel):
    topic_id: Optional[str] = None
    activity_type: str

class StudySessionComplete(BaseModel):
    duration: int
    completion_status: str

class StudySessionResponse(StudySessionCreate):
    id: str
    user_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration: int
    completion_status: str

    class Config:
        from_attributes = True

class LearningAnalytics(BaseModel):
    total_learning_time_seconds: int
    questions_solved: int
    average_accuracy: float
    current_streak: int
    topics_mastered: int
    weak_topics: List[str] # List of topic IDs or names

class RecommendationItem(BaseModel):
    type: str
    topic: str
    priority: str
    reason: str
    action: str
