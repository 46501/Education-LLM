from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta, timezone
from ..models.personalization import RevisionSchedule

async def update_revision_schedule(db: AsyncSession, user_id: str, topic_id: str, accuracy: float):
    # SM-2 inspired simple spaced repetition
    query = select(RevisionSchedule).where(
        RevisionSchedule.user_id == user_id,
        RevisionSchedule.topic_id == topic_id
    )
    result = await db.execute(query)
    schedule = result.scalar_one_or_none()

    if not schedule:
        # First time practicing this topic
        schedule = RevisionSchedule(
            user_id=user_id,
            topic_id=topic_id,
            last_reviewed=datetime.now(timezone.utc),
            interval_days=1.0,
            review_count=1,
            ease_score=2.5,
            status="UPCOMING"
        )
        schedule.next_review = schedule.last_reviewed + timedelta(days=schedule.interval_days)
        db.add(schedule)
        await db.commit()
        return schedule

    # Update existing schedule based on accuracy
    schedule.last_reviewed = datetime.now(timezone.utc)
    schedule.review_count += 1
    
    # Calculate quality from accuracy (0 to 5)
    quality = accuracy / 20.0 
    
    if quality < 3:
        # Poor performance, reset interval
        schedule.interval_days = 1.0
        schedule.status = "DUE"
    else:
        # Good performance, increase interval and ease score
        schedule.ease_score = schedule.ease_score + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        if schedule.ease_score < 1.3:
            schedule.ease_score = 1.3
        
        if schedule.review_count == 1:
            schedule.interval_days = 1.0
        elif schedule.review_count == 2:
            schedule.interval_days = 6.0
        else:
            schedule.interval_days = schedule.interval_days * schedule.ease_score

        if schedule.interval_days > 365:
            schedule.interval_days = 365
            schedule.status = "MASTERED"
        else:
            schedule.status = "UPCOMING"

    schedule.next_review = schedule.last_reviewed + timedelta(days=schedule.interval_days)
    await db.commit()
    return schedule

async def get_due_revisions(db: AsyncSession, user_id: str, limit: int = 5):
    now = datetime.now(timezone.utc)
    query = select(RevisionSchedule).where(
        RevisionSchedule.user_id == user_id,
        RevisionSchedule.next_review <= now,
        RevisionSchedule.status != "MASTERED"
    ).order_by(RevisionSchedule.next_review).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()
