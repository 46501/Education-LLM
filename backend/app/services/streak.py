from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func as sql_func
from datetime import datetime, timezone, date
from ..models.personalization import LearningProfile, StudySession
from ..models.learning import TopicMastery


async def update_streak(db: AsyncSession, user_id: str):
    """
    Update the learning streak for a user.

    A streak counts meaningful completed learning activities (not logins).
    A "meaningful activity" is defined as:
      - Completing a quiz
      - Completing a practice question
      - Completing a revision session
      - Completing a study session

    The streak increments if the user has completed at least one meaningful
    activity today. It resets if the user missed an entire calendar day
    (UTC-based) since their last active date.
    """
    # Get or create profile
    result = await db.execute(
        select(LearningProfile).where(LearningProfile.user_id == user_id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        profile = LearningProfile(user_id=user_id, current_streak=0, longest_streak=0)
        db.add(profile)

    today = datetime.now(timezone.utc).date()

    if profile.last_active_date:
        last_active = profile.last_active_date
        # Handle both datetime and date types
        if hasattr(last_active, 'date'):
            last_active_date = last_active.date()
        else:
            last_active_date = last_active

        if last_active_date == today:
            # Already active today — no change to streak
            return profile

        days_gap = (today - last_active_date).days

        if days_gap == 1:
            # Consecutive day — extend streak
            profile.current_streak += 1
        elif days_gap > 1:
            # Missed at least one full day — reset streak
            profile.current_streak = 1
    else:
        # First ever activity
        profile.current_streak = 1

    # Update longest streak
    if profile.current_streak > profile.longest_streak:
        profile.longest_streak = profile.current_streak

    profile.last_active_date = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(profile)
    return profile


async def get_learning_analytics(db: AsyncSession, user_id: str) -> dict:
    """
    Compute comprehensive learning analytics for a user.
    """
    # Get profile for streak info
    profile_result = await db.execute(
        select(LearningProfile).where(LearningProfile.user_id == user_id)
    )
    profile = profile_result.scalar_one_or_none()

    # Get total learning time from study sessions
    time_result = await db.execute(
        select(sql_func.coalesce(sql_func.sum(StudySession.duration), 0)).where(
            StudySession.user_id == user_id,
            StudySession.completion_status == "COMPLETED"
        )
    )
    total_learning_time = time_result.scalar() or 0

    # Get mastery stats
    mastery_result = await db.execute(
        select(TopicMastery).where(TopicMastery.user_id == user_id)
    )
    all_mastery = mastery_result.scalars().all()

    total_questions = sum(m.questions_attempted for m in all_mastery)
    avg_accuracy = (
        sum(m.accuracy for m in all_mastery) / len(all_mastery)
        if all_mastery else 0.0
    )
    topics_mastered = sum(1 for m in all_mastery if m.mastery_score >= 80)
    weak_topics = [m.topic_id for m in all_mastery if m.accuracy < 60]

    # Get total study sessions count
    session_count_result = await db.execute(
        select(sql_func.count(StudySession.id)).where(
            StudySession.user_id == user_id,
            StudySession.completion_status == "COMPLETED"
        )
    )
    total_sessions = session_count_result.scalar() or 0

    return {
        "total_learning_time_seconds": total_learning_time,
        "questions_solved": total_questions,
        "average_accuracy": round(avg_accuracy, 1),
        "current_streak": profile.current_streak if profile else 0,
        "longest_streak": profile.longest_streak if profile else 0,
        "topics_mastered": topics_mastered,
        "total_topics_attempted": len(all_mastery),
        "weak_topics": weak_topics,
        "total_study_sessions": total_sessions,
    }
