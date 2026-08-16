from sqlalchemy import Column, String, DateTime, func, ForeignKey, Integer, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from ..core.database import Base
import uuid

class Interview(Base):
    __tablename__ = "interviews"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    interview_type = Column(String, nullable=False) # TECHNICAL, CODING, HR, ML, DATA_SCIENCE
    role = Column(String, nullable=False)
    experience_level = Column(String, nullable=False) # ENTRY, MID, SENIOR
    topics = Column(JSONB, nullable=True) # Array of topics/skills
    difficulty = Column(String, default="MEDIUM")
    num_questions = Column(Integer, default=5)
    status = Column(String, default="CREATED") # CREATED, IN_PROGRESS, COMPLETED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    sessions = relationship("InterviewSession", back_populates="interview", cascade="all, delete-orphan")

class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    interview_id = Column(String, ForeignKey("interviews.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default="IN_PROGRESS") # IN_PROGRESS, COMPLETED, ABANDONED
    score = Column(Float, nullable=True) # 0 to 10
    feedback = Column(JSONB, nullable=True) # Overall strengths, weaknesses, communication

    interview = relationship("Interview", back_populates="sessions")
    messages = relationship("InterviewMessage", back_populates="session", cascade="all, delete-orphan")

class InterviewMessage(Base):
    __tablename__ = "interview_messages"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("interview_sessions.id"), nullable=False)
    role = Column(String, nullable=False) # interviewer, student
    content = Column(String, nullable=False)
    evaluation = Column(JSONB, nullable=True) # if role == student, stores the AI's structured evaluation of this specific answer
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("InterviewSession", back_populates="messages")
