from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from ..core.database import get_db
from ..models.user import User
from ..models.learning import TopicMastery, Mistake, Topic
from ..services.recommendation import recommendation_engine
from .deps import get_current_user

router = APIRouter()

@router.get("/mastery")
async def get_mastery(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(TopicMastery).options(selectinload(TopicMastery.topic)).where(TopicMastery.user_id == current_user.id)
    result = await db.execute(stmt)
    mastery_records = result.scalars().all()

    data = []
    for m in mastery_records:
        data.append({
            "topic_id": m.topic_id,
            "topic_name": m.topic.name,
            "mastery_score": m.mastery_score,
            "accuracy": m.accuracy,
            "current_difficulty": m.current_difficulty,
            "questions_attempted": m.questions_attempted
        })
    return {"mastery": data}

@router.get("/mistakes")
async def get_mistakes(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(Mistake).options(selectinload(Mistake.topic), selectinload(Mistake.question)).where(Mistake.user_id == current_user.id).order_by(Mistake.created_at.desc()).limit(20)
    result = await db.execute(stmt)
    mistakes = result.scalars().all()

    data = []
    for m in mistakes:
        data.append({
            "id": m.id,
            "topic": m.topic.name,
            "question": m.question.question_text,
            "student_answer": m.student_answer,
            "correct_answer": m.question.correct_answer,
            "error_category": m.error_category,
            "explanation": m.explanation,
            "timestamp": m.created_at
        })
    return {"mistakes": data}

@router.get("/recommendations")
async def get_recommendations(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    recs = await recommendation_engine.generate_recommendations(db, current_user.id)
    return {"recommendations": recs}
