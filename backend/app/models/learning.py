from sqlalchemy import Column, String, DateTime, func, ForeignKey, Integer, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from ..core.database import Base
import uuid

class Subject(Base):
    __tablename__ = "subjects"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)

class Topic(Base):
    __tablename__ = "topics"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    subject_id = Column(String, ForeignKey("subjects.id"), nullable=False)
    name = Column(String, nullable=False)
    parent_topic_id = Column(String, ForeignKey("topics.id"), nullable=True)
    
    subject = relationship("Subject")

class Question(Base):
    __tablename__ = "questions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    subject_id = Column(String, ForeignKey("subjects.id"), nullable=False)
    topic_id = Column(String, ForeignKey("topics.id"), nullable=False)
    question_text = Column(String, nullable=False)
    question_type = Column(String, nullable=False) # MCQ, MULTIPLE_CORRECT, TRUE_FALSE, SHORT_ANSWER, NUMERICAL
    difficulty = Column(String, nullable=False) # BEGINNER, EASY, MEDIUM, HARD, EXPERT
    options = Column(JSONB, nullable=True) # Array of options for MCQ
    correct_answer = Column(JSONB, nullable=False) # String, Array, or numeric range depending on type
    explanation = Column(String, nullable=True)
    source_document_id = Column(String, ForeignKey("documents.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Quiz(Base):
    __tablename__ = "quizzes"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    subject_id = Column(String, ForeignKey("subjects.id"), nullable=True)
    topic_id = Column(String, ForeignKey("topics.id"), nullable=True)
    difficulty = Column(String, nullable=True)
    number_of_questions = Column(Integer, nullable=False)
    status = Column(String, default="CREATED") # CREATED, IN_PROGRESS, COMPLETED, ABANDONED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("QuestionAttempt", back_populates="quiz", cascade="all, delete-orphan")

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    quiz_id = Column(String, ForeignKey("quizzes.id"), primary_key=True)
    question_id = Column(String, ForeignKey("questions.id"), primary_key=True)
    question_order = Column(Integer, nullable=False)
    marks = Column(Float, default=1.0)

    quiz = relationship("Quiz", back_populates="questions")
    question = relationship("Question")

class QuestionAttempt(Base):
    __tablename__ = "question_attempts"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    quiz_id = Column(String, ForeignKey("quizzes.id"), nullable=True) # Null for practice mode
    question_id = Column(String, ForeignKey("questions.id"), nullable=False)
    submitted_answer = Column(JSONB, nullable=True)
    is_correct = Column(Boolean, nullable=False, default=False)
    score = Column(Float, nullable=False, default=0.0)
    max_score = Column(Float, nullable=False, default=1.0)
    evaluation_feedback = Column(JSONB, nullable=True) # {score, missing_points, feedback, etc}
    time_taken = Column(Integer, nullable=True) # in seconds
    attempted_at = Column(DateTime(timezone=True), server_default=func.now())

    quiz = relationship("Quiz", back_populates="attempts")
    question = relationship("Question")

class TopicMastery(Base):
    __tablename__ = "topic_mastery"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    topic_id = Column(String, ForeignKey("topics.id"), nullable=False)
    mastery_score = Column(Float, default=0.0) # 0 to 100
    questions_attempted = Column(Integer, default=0)
    questions_correct = Column(Integer, default=0)
    questions_incorrect = Column(Integer, default=0)
    accuracy = Column(Float, default=0.0) # 0 to 100
    current_difficulty = Column(String, default="BEGINNER")
    last_practiced = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    topic = relationship("Topic")

class Mistake(Base):
    __tablename__ = "mistakes"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    topic_id = Column(String, ForeignKey("topics.id"), nullable=False)
    question_id = Column(String, ForeignKey("questions.id"), nullable=False)
    error_category = Column(String, nullable=False) # CONCEPTUAL_ERROR, CALCULATION_ERROR, CARELESS_ERROR, etc.
    student_answer = Column(JSONB, nullable=True)
    explanation = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    topic = relationship("Topic")
    question = relationship("Question")
