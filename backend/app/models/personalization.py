from sqlalchemy import Column, String, DateTime, func, ForeignKey, Integer, Float
from sqlalchemy.orm import relationship
from ..core.database import Base
import uuid

class LearningProfile(Base):
    __tablename__ = "learning_profiles"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_active_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class LearningPreference(Base):
    __tablename__ = "learning_preferences"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True)
    explanation_style = Column(String, default="Balanced") # Concise, Detailed, Step-by-step, Example-first, Exam-oriented
    practice_preference = Column(String, default="Balanced") # More theory, More MCQs, More coding, More numerical
    difficulty_preference = Column(String, default="Balanced") # Beginner, Balanced, Challenging
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class LearningMemory(Base):
    __tablename__ = "learning_memories"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    memory_type = Column(String, nullable=False) # STRENGTH, WEAKNESS, PREFERENCE, GOAL, MISCONCEPTION, ACHIEVEMENT, LEARNING_PATTERN
    topic_id = Column(String, ForeignKey("topics.id"), nullable=True)
    content = Column(String, nullable=False)
    confidence = Column(Float, default=1.0) # 0.0 to 1.0
    source = Column(String, nullable=True) # Source of memory, e.g., 'QUIZ_ATTEMPT', 'CHAT'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class StudyPlan(Base):
    __tablename__ = "study_plans"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    goal = Column(String, nullable=True)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default="ACTIVE") # ACTIVE, COMPLETED, ABANDONED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    items = relationship("StudyPlanItem", back_populates="plan", cascade="all, delete-orphan")

class StudyPlanItem(Base):
    __tablename__ = "study_plan_items"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    plan_id = Column(String, ForeignKey("study_plans.id"), nullable=False)
    topic_id = Column(String, ForeignKey("topics.id"), nullable=True)
    activity_type = Column(String, nullable=False) # LEARN, PRACTICE, REVISION, QUIZ, MOCK_TEST
    estimated_minutes = Column(Integer, default=15)
    priority = Column(String, default="MEDIUM") # HIGH, MEDIUM, LOW
    scheduled_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default="PENDING") # PENDING, IN_PROGRESS, COMPLETED
    completed_at = Column(DateTime(timezone=True), nullable=True)

    plan = relationship("StudyPlan", back_populates="items")

class RevisionSchedule(Base):
    __tablename__ = "revision_schedules"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    topic_id = Column(String, ForeignKey("topics.id"), nullable=False)
    last_reviewed = Column(DateTime(timezone=True), nullable=True)
    next_review = Column(DateTime(timezone=True), nullable=False)
    interval_days = Column(Float, default=1.0)
    review_count = Column(Integer, default=0)
    ease_score = Column(Float, default=2.5) # Based on SM-2 algorithm
    status = Column(String, default="DUE") # DUE, UPCOMING, MASTERED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class TopicPrerequisite(Base):
    __tablename__ = "topic_prerequisites"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    topic_id = Column(String, ForeignKey("topics.id"), nullable=False)
    prerequisite_topic_id = Column(String, ForeignKey("topics.id"), nullable=False)

class StudySession(Base):
    __tablename__ = "study_sessions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    topic_id = Column(String, ForeignKey("topics.id"), nullable=True)
    activity_type = Column(String, nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration = Column(Integer, default=0) # In seconds
    completion_status = Column(String, default="IN_PROGRESS") # IN_PROGRESS, COMPLETED, ABANDONED
