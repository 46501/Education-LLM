from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta, timezone
from ..models.personalization import RevisionSchedule

# Adaptive interval progression levels.
# On consistent good performance, the interval grows through these stages.
# Poor performance drops back toward the beginning of the sequence.
INTERVAL_LADDER = [1.0, 3.0, 7.0, 14.0, 30.0, 60.0, 120.0, 365.0]

# Quality thresholds (accuracy 0-100 scale)
GOOD_THRESHOLD = 60.0    # >= 60% accuracy is "passing"
GREAT_THRESHOLD = 85.0   # >= 85% is "great", advances faster
POOR_THRESHOLD = 40.0    # < 40% resets more aggressively


def _next_interval(current_interval: float, accuracy: float, ease: float) -> tuple[float, float, str]:
    """
    Calculate the next review interval based on current interval, accuracy, and ease.

    Returns (new_interval_days, new_ease_score, new_status).
    """
    # Determine where we are on the ladder
    current_rung = 0
    for i, val in enumerate(INTERVAL_LADDER):
        if current_interval >= val:
            current_rung = i

    if accuracy < POOR_THRESHOLD:
        # Poor performance — drop back to first rung
        new_interval = INTERVAL_LADDER[0]
        new_ease = max(1.3, ease - 0.20)
        return new_interval, new_ease, "DUE"

    elif accuracy < GOOD_THRESHOLD:
        # Mediocre performance — stay at current rung or drop by one
        target_rung = max(0, current_rung - 1)
        new_interval = INTERVAL_LADDER[target_rung]
        new_ease = max(1.3, ease - 0.10)
        return new_interval, new_ease, "UPCOMING"

    elif accuracy < GREAT_THRESHOLD:
        # Good performance — advance one rung
        target_rung = min(len(INTERVAL_LADDER) - 1, current_rung + 1)
        new_interval = INTERVAL_LADDER[target_rung]
        new_ease = ease + 0.05
        status = "MASTERED" if new_interval >= 365.0 else "UPCOMING"
        return new_interval, new_ease, status

    else:
        # Great performance — advance two rungs
        target_rung = min(len(INTERVAL_LADDER) - 1, current_rung + 2)
        new_interval = INTERVAL_LADDER[target_rung]
        new_ease = ease + 0.10
        status = "MASTERED" if new_interval >= 365.0 else "UPCOMING"
        return new_interval, new_ease, status


async def update_revision_schedule(db: AsyncSession, user_id: str, topic_id: str, accuracy: float) -> RevisionSchedule:
    """
    Update or create a revision schedule entry for a user-topic pair.
    Uses an adaptive interval ladder: 1 → 3 → 7 → 14 → 30 → 60 → 120 → 365 days,
    adjusted by accuracy on each review.
    """
    query = select(RevisionSchedule).where(
        RevisionSchedule.user_id == user_id,
        RevisionSchedule.topic_id == topic_id
    )
    result = await db.execute(query)
    schedule = result.scalar_one_or_none()
    now = datetime.now(timezone.utc)

    if not schedule:
        # First encounter with this topic — start at 1 day
        initial_interval = INTERVAL_LADDER[0]
        schedule = RevisionSchedule(
            user_id=user_id,
            topic_id=topic_id,
            last_reviewed=now,
            next_review=now + timedelta(days=initial_interval),
            interval_days=initial_interval,
            review_count=1,
            ease_score=2.5,
            status="UPCOMING"
        )
        db.add(schedule)
        await db.commit()
        await db.refresh(schedule)
        return schedule

    # Calculate new interval
    new_interval, new_ease, new_status = _next_interval(
        schedule.interval_days, accuracy, schedule.ease_score
    )

    schedule.last_reviewed = now
    schedule.review_count += 1
    schedule.interval_days = new_interval
    schedule.ease_score = new_ease
    schedule.status = new_status
    schedule.next_review = now + timedelta(days=new_interval)

    await db.commit()
    await db.refresh(schedule)
    return schedule


async def get_due_revisions(db: AsyncSession, user_id: str, limit: int = 10) -> list:
    """Return topics that are due for revision (next_review <= now and not MASTERED)."""
    now = datetime.now(timezone.utc)
    query = (
        select(RevisionSchedule)
        .where(
            RevisionSchedule.user_id == user_id,
            RevisionSchedule.next_review <= now,
            RevisionSchedule.status != "MASTERED"
        )
        .order_by(RevisionSchedule.next_review)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()


async def get_all_schedules(db: AsyncSession, user_id: str) -> list:
    """Return all revision schedules for a user."""
    query = (
        select(RevisionSchedule)
        .where(RevisionSchedule.user_id == user_id)
        .order_by(RevisionSchedule.next_review)
    )
    result = await db.execute(query)
    return result.scalars().all()
