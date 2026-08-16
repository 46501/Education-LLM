from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone, timedelta
from ..models.user import User

async def award_xp(db: AsyncSession, user_id: str, amount: int) -> dict:
    """
    Awards XP to a user and calculates daily streak.
    Returns a dict with updated xp, streak info, and whether they leveled up/gained streak.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        return {"error": "User not found"}
        
    now = datetime.now(timezone.utc)
    streak_updated = False
    
    # Calculate streak
    if user.last_active_date:
        last_active = user.last_active_date.replace(tzinfo=timezone.utc)
        
        # Strip time for date comparison
        today = now.date()
        last_date = last_active.date()
        delta = today - last_date
        
        if delta == timedelta(days=1):
            user.current_streak += 1
            streak_updated = True
        elif delta > timedelta(days=1):
            user.current_streak = 1 # Reset streak
            streak_updated = True
    else:
        user.current_streak = 1
        streak_updated = True
        
    user.xp += amount
    user.last_active_date = now
    
    await db.commit()
    await db.refresh(user)
    
    return {
        "xp": user.xp,
        "xp_gained": amount,
        "current_streak": user.current_streak,
        "streak_updated": streak_updated
    }
