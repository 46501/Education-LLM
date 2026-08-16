from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.personalization import StudyPlan, StudyPlanItem, RevisionSchedule, LearningMemory
from ..models.learning import TopicMastery, Topic
from typing import List, Dict, Optional
import litellm
from ..core.config import settings
import json
from datetime import datetime, timedelta, timezone


async def generate_study_plan_context(db: AsyncSession, user_id: str) -> dict:
    """Collect student context for study plan generation."""
    # Get due revisions
    rev_query = select(RevisionSchedule).where(
        RevisionSchedule.user_id == user_id,
        RevisionSchedule.status == "DUE"
    )
    due_revisions = (await db.execute(rev_query)).scalars().all()

    # Get weak topics (accuracy < 60%)
    weak_query = select(TopicMastery).where(
        TopicMastery.user_id == user_id,
        TopicMastery.accuracy < 60.0
    )
    weak_topics = (await db.execute(weak_query)).scalars().all()

    # Get strong topics for reference
    strong_query = select(TopicMastery).where(
        TopicMastery.user_id == user_id,
        TopicMastery.accuracy >= 80.0
    )
    strong_topics = (await db.execute(strong_query)).scalars().all()

    # Get learning memories (weaknesses and misconceptions)
    mem_query = select(LearningMemory).where(
        LearningMemory.user_id == user_id,
        LearningMemory.memory_type.in_(["WEAKNESS", "MISCONCEPTION"])
    )
    memories = (await db.execute(mem_query)).scalars().all()

    # Get all topics for name resolution
    topics = (await db.execute(select(Topic))).scalars().all()
    topic_map = {t.id: t.name for t in topics}

    context = {
        "due_revisions": [
            {"topic_id": r.topic_id, "topic_name": topic_map.get(r.topic_id, r.topic_id)}
            for r in due_revisions
        ],
        "weak_topics": [
            {
                "topic_id": w.topic_id,
                "topic_name": topic_map.get(w.topic_id, w.topic_id),
                "accuracy": w.accuracy,
                "mastery": w.mastery_score
            }
            for w in weak_topics
        ],
        "strong_topics": [
            {"topic_id": s.topic_id, "topic_name": topic_map.get(s.topic_id, s.topic_id)}
            for s in strong_topics
        ],
        "issues": [
            {"type": m.memory_type, "content": m.content}
            for m in memories
        ],
        "topic_map": topic_map,
    }
    return context


async def generate_study_plan_with_llm(
    db: AsyncSession,
    user_id: str,
    goal: str,
    duration_days: int,
    available_minutes: int
) -> Optional[dict]:
    """
    Generate a study plan using LLM.
    Falls back to a deterministic plan when LLM is unavailable.
    """
    context = await generate_study_plan_context(db, user_id)

    prompt = f"""
    You are an AI Study Planner. Create a study plan for {duration_days} days,
    maximum {available_minutes} minutes per day.
    Goal: {goal}

    Student Context:
    Due Revisions: {json.dumps(context['due_revisions'])}
    Weak Topics: {json.dumps(context['weak_topics'])}
    Strong Topics (no need to focus): {json.dumps(context['strong_topics'])}
    Known Issues: {json.dumps(context['issues'])}

    Return a JSON response strictly matching this schema:
    {{
        "title": "Plan Title",
        "items": [
            {{
                "topic_name": "string",
                "activity_type": "LEARN or PRACTICE or REVISION or QUIZ",
                "estimated_minutes": 15,
                "priority": "HIGH or MEDIUM or LOW",
                "day": 1
            }}
        ]
    }}

    Rules:
    1. Due revisions should always be HIGH priority and placed early.
    2. Weak topics get PRACTICE activities.
    3. Total minutes per day must not exceed {available_minutes}.
    4. Spread activities across the {duration_days} days.
    """

    # Check if we have a real API key
    if not settings.LLM_API_KEY or settings.LLM_API_KEY == "your_openai_api_key_here":
        # Deterministic fallback plan
        return _generate_fallback_plan(context, goal, duration_days, available_minutes)

    try:
        response = await litellm.acompletion(
            model="gemini/gemini-1.5-pro",
            api_key=settings.LLM_API_KEY,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        print(f"LLM Error generating study plan: {e}")
        # Fall back to deterministic plan
        return _generate_fallback_plan(context, goal, duration_days, available_minutes)


def _generate_fallback_plan(context: dict, goal: str, duration_days: int, available_minutes: int) -> dict:
    """Generate a deterministic study plan when LLM is unavailable."""
    items = []
    day = 1

    # Schedule revisions first (highest priority)
    for rev in context.get("due_revisions", []):
        if day > duration_days:
            break
        items.append({
            "topic_name": rev["topic_name"],
            "activity_type": "REVISION",
            "estimated_minutes": min(20, available_minutes),
            "priority": "HIGH",
            "day": day,
        })
        day += 1

    # Schedule weak topic practice
    for weak in context.get("weak_topics", []):
        if day > duration_days:
            day = 1  # Wrap around
        items.append({
            "topic_name": weak["topic_name"],
            "activity_type": "PRACTICE",
            "estimated_minutes": min(25, available_minutes),
            "priority": "HIGH",
            "day": day,
        })
        day += 1

    # If no specific items, create a generic learning item
    if not items:
        items.append({
            "topic_name": "General Review",
            "activity_type": "LEARN",
            "estimated_minutes": min(30, available_minutes),
            "priority": "MEDIUM",
            "day": 1,
        })

    return {
        "title": f"Study Plan: {goal[:60]}",
        "items": items
    }


async def create_study_plan_from_data(
    db: AsyncSession,
    user_id: str,
    plan_data: dict,
    goal: str,
    duration_days: int
) -> StudyPlan:
    """
    Persist a study plan and its items to the database.
    Resolves topic names to IDs where possible.
    """
    now = datetime.now(timezone.utc)

    # Get topic name -> id mapping
    topics = (await db.execute(select(Topic))).scalars().all()
    name_to_id = {t.name.lower(): t.id for t in topics}

    plan = StudyPlan(
        user_id=user_id,
        title=plan_data.get("title", f"Study Plan: {goal[:60]}"),
        goal=goal,
        start_date=now,
        end_date=now + timedelta(days=duration_days),
        status="ACTIVE"
    )
    db.add(plan)
    await db.flush()

    for item_data in plan_data.get("items", []):
        topic_name = item_data.get("topic_name", "")
        topic_id = name_to_id.get(topic_name.lower()) if topic_name else None
        day = item_data.get("day", 1)

        plan_item = StudyPlanItem(
            plan_id=plan.id,
            topic_id=topic_id,
            activity_type=item_data.get("activity_type", "LEARN"),
            estimated_minutes=item_data.get("estimated_minutes", 15),
            priority=item_data.get("priority", "MEDIUM"),
            scheduled_date=now + timedelta(days=day - 1),
            status="PENDING"
        )
        db.add(plan_item)

    await db.commit()
    await db.refresh(plan)
    return plan


async def get_active_study_plans(db: AsyncSession, user_id: str) -> list[StudyPlan]:
    """Get all active study plans for a user."""
    result = await db.execute(
        select(StudyPlan)
        .where(StudyPlan.user_id == user_id, StudyPlan.status == "ACTIVE")
        .order_by(StudyPlan.created_at.desc())
    )
    return result.scalars().all()
