from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
import uuid
import logging

logger = logging.getLogger(__name__)
from ..core.database import get_db
from ..models.user import User
from ..models.learning import Subject, Topic, Question, QuestionAttempt
from ..services.quiz_generator import quiz_generator
from ..services.evaluator import answer_evaluator
from ..services.scoring import scoring_engine
from .deps import get_current_user

router = APIRouter()

class StartPracticeRequest(BaseModel):
    subject: str
    topic: str
    difficulty: str

class PracticeAnswerRequest(BaseModel):
    question_id: str
    submitted_answer: str

@router.post("/start")
async def start_practice(req: StartPracticeRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # Same logic as quiz generation but we only fetch/generate 1 question
    result = await db.execute(select(Subject).where(Subject.name == req.subject))
    subj = result.scalars().first()
    if not subj:
        subj = Subject(name=req.subject)
        db.add(subj)
        await db.flush()

    result = await db.execute(select(Topic).where(Topic.name == req.topic, Topic.subject_id == subj.id))
    topic = result.scalars().first()
    if not topic:
        topic = Topic(name=req.topic, subject_id=subj.id)
        db.add(topic)
        await db.flush()

    generation_response = await quiz_generator.generate_questions(
        db=db,
        user_id=current_user.id,
        subject=req.subject,
        topic=req.topic,
        difficulty=req.difficulty,
        num_questions=1,
        question_type="MCQ",
        use_rag=False
    )

    q_data = generation_response.questions[0]
    question = Question(
        subject_id=subj.id,
        topic_id=topic.id,
        question_text=q_data.question_text,
        question_type="MCQ",
        difficulty=q_data.difficulty,
        options=q_data.options,
        correct_answer=q_data.correct_answer,
        explanation=q_data.explanation
    )
    db.add(question)
    await db.commit()

    return {
        "id": question.id,
        "text": question.question_text,
        "options": question.options,
        "type": question.question_type
    }

@router.post("/answer")
async def answer_practice(req: PracticeAnswerRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Question).where(Question.id == req.question_id))
    q = result.scalars().first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    eval_res = answer_evaluator.evaluate_mcq(req.submitted_answer, q.correct_answer)
    
    attempt = QuestionAttempt(
        user_id=current_user.id,
        quiz_id=None, # Practice mode has no quiz
        question_id=q.id,
        submitted_answer=req.submitted_answer,
        is_correct=eval_res["is_correct"],
        score=eval_res["score"],
        evaluation_feedback=eval_res
    )
    db.add(attempt)

    # Update Mastery
    mastery = await scoring_engine.update_mastery(db, current_user.id, q.topic_id, eval_res["is_correct"], q.difficulty)

    if not eval_res["is_correct"]:
        from ..models.learning import Mistake
        mistake_res = await answer_evaluator.classify_mistake(q.subject_id, q.question_text, q.correct_answer, req.submitted_answer) # Passed subject_id as topic placeholder
        mistake = Mistake(
            user_id=current_user.id,
            topic_id=q.topic_id,
            question_id=q.id,
            error_category=mistake_res.get("category", "UNKNOWN"),
            student_answer=req.submitted_answer,
            explanation=mistake_res.get("explanation", "Practice mistake.")
        )
        db.add(mistake)

    await db.commit()

    # --- Phase 4 Personalization Integration ---
    try:
        from ..services.spaced_repetition import update_revision_schedule
        from ..services.learning_memory import evaluate_and_store_memory
        from ..services.streak import update_streak

        # Use the single question's accuracy (100 or 0)
        accuracy = 100.0 if eval_res["is_correct"] else 0.0
        await update_revision_schedule(db, current_user.id, q.topic_id, accuracy)
        await evaluate_and_store_memory(db, current_user.id, q.topic_id)

        # Practice answer is a meaningful learning activity
        await update_streak(db, current_user.id)
        
        # --- Gamification ---
        from ..services.gamification import award_xp
        xp_gained = 5 if eval_res["is_correct"] else 1
        gamification_result = await award_xp(db, current_user.id, xp_gained)
        
    except Exception as e:
        logger.error(f"Phase 4 post-practice integration error (non-fatal): {e}")

    return {
        "is_correct": eval_res["is_correct"],
        "correct_answer": q.correct_answer,
        "explanation": q.explanation,
        "new_recommended_difficulty": mastery.current_difficulty,
        "gamification": gamification_result if 'gamification_result' in locals() else None
    }
