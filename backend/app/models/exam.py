from sqlalchemy import Column, String, DateTime, func, ForeignKey, Integer, Float
from sqlalchemy.orm import relationship
from ..core.database import Base
import uuid

class Exam(Base):
    __tablename__ = "exams"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    exam_date = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, nullable=False, default=60)
    total_marks = Column(Float, nullable=False, default=100.0)
    status = Column(String, default="DRAFT") # DRAFT, ACTIVE, COMPLETED, ARCHIVED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    topics = relationship("ExamTopic", back_populates="exam", cascade="all, delete-orphan")
    questions = relationship("ExamQuestion", back_populates="exam", cascade="all, delete-orphan")
    sessions = relationship("ExamSession", back_populates="exam", cascade="all, delete-orphan")

class ExamTopic(Base):
    __tablename__ = "exam_topics"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    exam_id = Column(String, ForeignKey("exams.id"), nullable=False)
    topic_id = Column(String, ForeignKey("topics.id"), nullable=False)
    weight = Column(Float, default=1.0) # Used to balance questions
    priority = Column(String, default="MEDIUM") # HIGH, MEDIUM, LOW

    exam = relationship("Exam", back_populates="topics")
    topic = relationship("Topic")

class ExamQuestion(Base):
    __tablename__ = "exam_questions"
    exam_id = Column(String, ForeignKey("exams.id"), primary_key=True)
    question_id = Column(String, ForeignKey("questions.id"), primary_key=True)
    question_order = Column(Integer, nullable=False)
    marks = Column(Float, default=1.0)

    exam = relationship("Exam", back_populates="questions")
    question = relationship("Question")

class ExamSession(Base):
    __tablename__ = "exam_sessions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    exam_id = Column(String, ForeignKey("exams.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    duration = Column(Integer, default=0) # Total time spent in seconds
    status = Column(String, default="IN_PROGRESS") # NOT_STARTED, IN_PROGRESS, SUBMITTED, EXPIRED
    score = Column(Float, nullable=True) # Final evaluated score

    exam = relationship("Exam", back_populates="sessions")
