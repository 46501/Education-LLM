from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List

from ..core.database import get_db
from .deps import get_current_user
from ..models.user import User
from ..models.personalization import (
    LearningProfile, LearningPreference, LearningMemory,
    StudyPlan, StudySession, RevisionSchedule
)
from ..schemas.personalization import (
    LearningProfileResponse, LearningPreferenceResponse, LearningPreferenceUpdate,
    LearningMemoryCreate, LearningMemoryResponse,
    StudyPlanResponse, StudyPlanGenerateRequest,
    RevisionScheduleResponse, RevisionCompleteRequest,
    StudySessionResponse, StudySessionCreate, StudySessionComplete,
    RecommendationItem, LearningAnalytics, LearningPathItem
)
from ..services.study_planner import generate_study_plan_with_llm, create_study_plan_from_data
from ..services.spaced_repetition import get_due_revisions, update_revision_schedule, get_all_schedules
from ..services.recommendation import get_personalized_recommendations, get_learning_path
from ..services.streak import update_streak, get_learning_analytics
from ..services.learning_memory import get_memories

router = APIRouter()


# --- Profile & Preferences ---

@router.get("/profile/learning", response_model=LearningProfileResponse)
async def get_learning_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the current user's learning profile (streaks, etc.)."""
    result = await db.execute(
        select(LearningProfile).where(LearningProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        profile = LearningProfile(user_id=current_user.id)
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    return profile


@router.put("/profile/preferences", response_model=LearningPreferenceResponse)
async def update_learning_preferences(
    prefs: LearningPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update learning preferences (explanation style, practice type, difficulty)."""
    result = await db.execute(
        select(LearningPreference).where(LearningPreference.user_id == current_user.id)
    )
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


# --- Learning Memory ---

@router.get("/memory", response_model=List[LearningMemoryResponse])
async def get_learning_memories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all learning memories for the current user."""
    return await get_memories(db, current_user.id)


@router.post("/memory", response_model=LearningMemoryResponse)
async def create_learning_memory(
    memory: LearningMemoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Manually create a learning memory (e.g., from chat insights)."""
    new_mem = LearningMemory(
        user_id=current_user.id,
        memory_type=memory.memory_type,
        topic_id=memory.topic_id,
        content=memory.content,
        confidence=memory.confidence,
        source=memory.source or "USER_INPUT"
    )
    db.add(new_mem)
    await db.commit()
    await db.refresh(new_mem)
    return new_mem


# --- Study Plans ---

@router.get("/study-plan", response_model=List[StudyPlanResponse])
async def get_study_plans(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all study plans for the current user."""
    result = await db.execute(
        select(StudyPlan)
        .options(selectinload(StudyPlan.items))
        .where(StudyPlan.user_id == current_user.id)
        .order_by(StudyPlan.created_at.desc())
    )
    return result.scalars().all()


@router.post("/study-plan/generate", response_model=StudyPlanResponse)
async def generate_study_plan(
    request: StudyPlanGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate an AI-powered study plan and persist it with items."""
    plan_data = await generate_study_plan_with_llm(
        db, current_user.id, request.goal,
        request.duration_days, request.available_minutes_per_day
    )
    if not plan_data:
        raise HTTPException(status_code=500, detail="Failed to generate study plan")

    plan = await create_study_plan_from_data(
        db, current_user.id, plan_data,
        request.goal, request.duration_days
    )

    # Reload with items
    result = await db.execute(
        select(StudyPlan)
        .options(selectinload(StudyPlan.items))
        .where(StudyPlan.id == plan.id)
    )
    return result.scalar_one()


# --- Revision (Spaced Repetition) ---

@router.get("/revision/due", response_model=List[RevisionScheduleResponse])
async def get_due_revisions_api(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get topics that are due for revision."""
    return await get_due_revisions(db, current_user.id)


@router.get("/revision/all", response_model=List[RevisionScheduleResponse])
async def get_all_revisions_api(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all revision schedules for the current user."""
    return await get_all_schedules(db, current_user.id)


@router.post("/revision/{topic_id}/complete", response_model=RevisionScheduleResponse)
async def complete_revision(
    topic_id: str,
    request: RevisionCompleteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark a topic revision as complete with an accuracy score."""
    schedule = await update_revision_schedule(
        db, current_user.id, topic_id, request.accuracy
    )

    # Update streak since revision is a meaningful activity
    await update_streak(db, current_user.id)

    return schedule


# --- Recommendations & Learning Path ---

@router.get("/recommendations", response_model=List[RecommendationItem])
async def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get personalized learning recommendations."""
    return await get_personalized_recommendations(db, current_user.id)


@router.get("/learning-path", response_model=List[LearningPathItem])
async def get_learning_path_api(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get an ordered learning path showing topic progression."""
    return await get_learning_path(db, current_user.id)


# --- Study Sessions ---

@router.get("/study-sessions", response_model=List[StudySessionResponse])
async def get_study_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all study sessions for the current user."""
    result = await db.execute(
        select(StudySession)
        .where(StudySession.user_id == current_user.id)
        .order_by(StudySession.started_at.desc())
    )
    return result.scalars().all()


@router.post("/study-sessions/start", response_model=StudySessionResponse)
async def start_study_session(
    session_req: StudySessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start a new study session."""
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
async def complete_study_session(
    session_id: str,
    session_data: StudySessionComplete,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Complete a study session and update streak."""
    result = await db.execute(
        select(StudySession).where(
            StudySession.id == session_id,
            StudySession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Study session not found")

    from datetime import datetime, timezone
    session.duration = session_data.duration
    session.completion_status = session_data.completion_status
    session.completed_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(session)

    # Update streak if the session was completed (meaningful activity)
    if session_data.completion_status == "COMPLETED":
        await update_streak(db, current_user.id)

    return session


# --- Learning Analytics ---

@router.get("/analytics/learning", response_model=LearningAnalytics)
async def get_learning_analytics_api(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive learning analytics for the current user."""
    return await get_learning_analytics(db, current_user.id)
