from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Dict, Any
from datetime import datetime, timezone

from ..core.database import get_db
from ..models.user import User
from ..models.exam import Exam, ExamTopic, ExamQuestion, ExamSession
from ..models.learning import QuestionAttempt, TopicMastery, Mistake
from ..schemas.exam import ExamCreate, ExamSessionResponse, ExamSubmitRequest, ExamResultResponse
from ..services.exam_engine import exam_engine
from .deps import get_current_user
from ..core.exceptions import ResourceNotFoundError, ValidationError, DatabaseError, ConflictError

router = APIRouter()

@router.post("")
async def create_exam(
    exam_data: ExamCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    exam = Exam(
        user_id=current_user.id,
        title=exam_data.title,
        description=exam_data.description,
        exam_date=exam_data.exam_date,
        duration_minutes=exam_data.duration_minutes,
        total_marks=exam_data.total_marks,
        status="DRAFT"
    )
    db.add(exam)
    await db.flush()
    
    for t in exam_data.topics:
        et = ExamTopic(
            exam_id=exam.id,
            topic_id=t.topic_id,
            weight=t.weight,
            priority=t.priority
        )
        db.add(et)
        
    await db.commit()
    return {"id": exam.id, "message": "Exam created successfully"}

@router.get("")
async def list_exams(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Exam).where(Exam.user_id == current_user.id))
    exams = result.scalars().all()
    
    # Calculate readiness for upcoming ones
    out = []
    for e in exams:
        edata = {
            "id": e.id,
            "title": e.title,
            "exam_date": e.exam_date,
            "status": e.status,
            "readiness_score": 0.0
        }
        if e.status in ["DRAFT", "ACTIVE"]:
            edata["readiness_score"] = await exam_engine.calculate_readiness(db, current_user.id, e.id)
        out.append(edata)
    return out

@router.get("/{exam_id}")
async def get_exam(
    exam_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Exam).options(selectinload(Exam.topics)).where(Exam.id == exam_id, Exam.user_id == current_user.id))
    exam = result.scalars().first()
    if not exam:
        raise ResourceNotFoundError("Exam not found")
        
    readiness = await exam_engine.calculate_readiness(db, current_user.id, exam.id)
    return {
        "id": exam.id,
        "title": exam.title,
        "exam_date": exam.exam_date,
        "duration_minutes": exam.duration_minutes,
        "total_marks": exam.total_marks,
        "status": exam.status,
        "readiness_score": readiness
    }

@router.post("/{exam_id}/generate")
async def generate_mock_test(
    exam_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # This will intelligently select/generate questions based on the ExamTopic weights
    exam = await exam_engine.generate_mock_exam(db, exam_id, current_user.id)
    exam.status = "ACTIVE"
    await db.commit()
    return {"message": "Mock exam generated successfully."}

@router.post("/{exam_id}/start")
async def start_exam_session(
    exam_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Exam).where(Exam.id == exam_id, Exam.user_id == current_user.id))
    exam = result.scalars().first()
    if not exam or exam.status != "ACTIVE":
        raise ValidationError("Exam not found or not active")
        
    session = ExamSession(
        exam_id=exam.id,
        user_id=current_user.id,
        status="IN_PROGRESS"
    )
    db.add(session)
    await db.commit()
    return {"session_id": session.id}

@router.get("/{exam_id}/session/{session_id}")
async def get_exam_session(
    exam_id: str,
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(ExamSession)
        .options(selectinload(ExamSession.exam).selectinload(Exam.questions).selectinload(ExamQuestion.question))
        .where(ExamSession.id == session_id, ExamSession.user_id == current_user.id)
    )
    session = result.scalars().first()
    if not session:
        raise ResourceNotFoundError("Session not found")
        
    questions = []
    for eq in sorted(session.exam.questions, key=lambda x: x.question_order):
        q = eq.question
        questions.append({
            "question_id": q.id,
            "question_text": q.question_text,
            "question_type": q.question_type,
            "difficulty": q.difficulty,
            "options": q.options,
            "marks": eq.marks,
            "question_order": eq.question_order
            # Do NOT expose correct_answer or explanation
        })
        
    return {
        "id": session.id,
        "exam_id": exam_id,
        "started_at": session.started_at,
        "duration_minutes": session.exam.duration_minutes,
        "status": session.status,
        "questions": questions
    }

@router.post("/{exam_id}/session/{session_id}/submit")
async def submit_exam(
    exam_id: str,
    session_id: str,
    submission: ExamSubmitRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        session = await exam_engine.evaluate_exam(db, session_id, current_user.id, [a.model_dump() for a in submission.answers])
        return {"message": "Exam submitted successfully", "session_id": session.id}
    except ValueError as e:
        raise ValidationError(str(e))
    except Exception:
        raise DatabaseError("Failed to submit exam. Please try again.")

@router.get("/{exam_id}/session/{session_id}/results")
async def get_exam_results(
    exam_id: str,
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Retrieve attempts and build detailed analytics
    result = await db.execute(
        select(ExamSession)
        .options(selectinload(ExamSession.exam))
        .where(ExamSession.id == session_id, ExamSession.user_id == current_user.id)
    )
    session = result.scalars().first()
    if not session or session.status != "SUBMITTED":
        raise ConflictError("Results not available")
        
    att_res = await db.execute(
        select(QuestionAttempt)
        .options(selectinload(QuestionAttempt.question))
        .where(QuestionAttempt.exam_id == exam_id, QuestionAttempt.user_id == current_user.id)
    )
    attempts = att_res.scalars().all()
    
    # Filter attempts that were just made (for this session basically)
    # Since exam_id maps to multiple sessions potentially, ideally we should link attempt to session_id.
    # We'll assume the latest attempt for each question in this exam is from this session.
    
    mistakes = []
    for att in attempts:
        if not att.is_correct:
            mistakes.append({
                "question_text": att.question.question_text,
                "student_answer": att.submitted_answer,
                "correct_answer": att.question.correct_answer,
                "explanation": att.question.explanation,
                "feedback": att.evaluation_feedback
            })
            
    return {
        "exam_session_id": session.id,
        "score": session.score,
        "total_marks": session.exam.total_marks,
        "percentage": (session.score / session.exam.total_marks * 100) if session.exam.total_marks else 0,
        "topic_analysis": [], # Placeholder for topic breakdown
        "difficulty_analysis": {}, # Placeholder
        "mistakes": mistakes,
        "recommendations": ["Review mistakes", "Take another mock exam"]
    }
