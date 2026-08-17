from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List

from ..core.database import get_db
from ..models.user import User
from ..models.interview import Interview, InterviewSession, InterviewMessage
from ..schemas.interview import InterviewSetupRequest, InterviewAnswerRequest
from ..services.interview_engine import interview_engine
from .deps import get_current_user
from ..core.exceptions import ResourceNotFoundError, ValidationError, DatabaseError

router = APIRouter()

@router.post("")
async def setup_interview(
    setup_data: InterviewSetupRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    interview = Interview(
        user_id=current_user.id,
        interview_type=setup_data.interview_type,
        role=setup_data.role,
        experience_level=setup_data.experience_level,
        topics=setup_data.topics,
        difficulty=setup_data.difficulty,
        num_questions=setup_data.num_questions
    )
    db.add(interview)
    await db.commit()
    return {"id": interview.id, "message": "Interview setup complete"}

@router.get("")
async def list_interviews(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Interview).where(Interview.user_id == current_user.id))
    return result.scalars().all()

@router.post("/{interview_id}/start")
async def start_interview(
    interview_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Interview).where(Interview.id == interview_id, Interview.user_id == current_user.id))
    interview = result.scalars().first()
    if not interview:
        raise ResourceNotFoundError("Interview not found")
        
    session = InterviewSession(
        interview_id=interview.id,
        user_id=current_user.id,
        status="IN_PROGRESS"
    )
    db.add(session)
    await db.flush()
    
    # First greeting from AI
    ai_msg = InterviewMessage(
        session_id=session.id,
        role="interviewer",
        content=f"Hello! I will be your interviewer today for the {interview.role} position. Are you ready to begin?"
    )
    db.add(ai_msg)
    await db.commit()
    
    return {"session_id": session.id, "initial_message": ai_msg.content}

@router.post("/session/{session_id}/answer")
async def answer_question(
    session_id: str,
    answer_data: InterviewAnswerRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        response = await interview_engine.process_answer(db, session_id, current_user.id, answer_data.answer)
        return response
    except ValueError as ve:
        raise ValidationError(str(ve))
    except Exception as e:
        raise DatabaseError("Failed to process interview answer. Please try again.")

@router.post("/session/{session_id}/complete")
async def complete_interview(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        session = await interview_engine.complete_interview(db, session_id, current_user.id)
        
        # --- Gamification ---
        from ..services.gamification import award_xp
        # Base XP for completing an interview, plus bonus based on score
        xp_gained = 50 + int((session.score or 0) / 2)
        gamification_result = await award_xp(db, current_user.id, xp_gained)
        
        return {
            "message": "Interview completed", 
            "score": session.score, 
            "feedback": session.feedback,
            "gamification": gamification_result
        }
    except ValueError as ve:
        raise ValidationError(str(ve))
    except Exception as e:
        raise DatabaseError("Failed to complete interview. Please try again.")
