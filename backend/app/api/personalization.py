from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from ..core.database import get_db
from .deps import get_current_user
from ..models.user import User
from ..models.personalization import LearningProfile, LearningPreference, LearningMemory, StudyPlan, StudySession
from ..schemas.personalization import (
    LearningProfileResponse, LearningPreferenceResponse, LearningPreferenceUpdate,
    LearningMemoryResponse, StudyPlanResponse, StudyPlanGenerateRequest,
    RevisionScheduleResponse, StudySessionResponse, StudySessionCreate, StudySessionComplete,
    RecommendationItem
)
from ..services.study_planner import generate_study_plan_with_llm
from ..services.spaced_repetition import get_due_revisions
from ..services.recommendation import get_personalized_recommendations

router = APIRouter()

@router.get("/profile/learning", response_model=LearningProfileResponse)
async def get_learning_profile(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LearningProfile).where(LearningProfile.user_id == current_user.id))
    profile = result.scalar_one_or_none()
    if not profile:
        profile = LearningProfile(user_id=current_user.id)
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    return profile

@router.put("/profile/preferences", response_model=LearningPreferenceResponse)
async def update_learning_preferences(prefs: LearningPreferenceUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LearningPreference).where(LearningPreference.user_id == current_user.id))
    db_prefs = result.scalar_one_or_none()
    
    if not db_prefs:
        db_prefs = LearningPreference(user_id=current_user.id)
        db.add(db_prefs)

    if prefs.explanation_style:
        db_prefs.explanation_style = prefs.explanation_style
    if prefs.practice_preference:
        db_prefs.practice_preference = prefs.practice_preference
    if prefs.difficulty_preference:
        db_prefs.difficulty_preference = prefs.difficulty_preference

    await db.commit()
    await db.refresh(db_prefs)
    return db_prefs

@router.get("/memory", response_model=List[LearningMemoryResponse])
async def get_learning_memories(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LearningMemory).where(LearningMemory.user_id == current_user.id))
    return result.scalars().all()

@router.post("/study-plan/generate", response_model=StudyPlanResponse)
async def generate_study_plan(request: StudyPlanGenerateRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    plan_data = await generate_study_plan_with_llm(
        db, current_user.id, request.goal, request.duration_days, request.available_minutes_per_day
    )
    if not plan_data:
        raise HTTPException(status_code=500, detail="Failed to generate study plan")
        
    plan = StudyPlan(user_id=current_user.id, title=plan_data["title"], goal=request.goal)
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    
    # Normally we would create StudyPlanItem records here, simplified for example
    return plan

@router.get("/revision/due", response_model=List[RevisionScheduleResponse])
async def get_due_revisions_api(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_due_revisions(db, current_user.id)

@router.get("/recommendations", response_model=List[RecommendationItem])
async def get_recommendations(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_personalized_recommendations(db, current_user.id)

@router.post("/study-sessions/start", response_model=StudySessionResponse)
async def start_study_session(session_req: StudySessionCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    session = StudySession(
        user_id=current_user.id,
        topic_id=session_req.topic_id,
        activity_type=session_req.activity_type
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session

@router.post("/study-sessions/{session_id}/complete", response_model=StudySessionResponse)
async def complete_study_session(session_id: str, session_data: StudySessionComplete, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(StudySession).where(StudySession.id == session_id, StudySession.user_id == current_user.id))
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Study session not found")
        
    session.duration = session_data.duration
    session.completion_status = session_data.completion_status
    from datetime import datetime, timezone
    session.completed_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(session)
    return session
