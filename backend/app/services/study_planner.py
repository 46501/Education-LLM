from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.personalization import StudyPlan, StudyPlanItem, RevisionSchedule, LearningMemory
from ..models.learning import TopicMastery, Topic
from typing import List, Dict
import litellm
from ..core.config import settings
import json

async def generate_study_plan_context(db: AsyncSession, user_id: str):
    # Get due revisions
    rev_query = select(RevisionSchedule).where(
        RevisionSchedule.user_id == user_id,
        RevisionSchedule.status == "DUE"
    )
    due_revisions = (await db.execute(rev_query)).scalars().all()

    # Get weak topics
    weak_query = select(TopicMastery).where(
        TopicMastery.user_id == user_id,
        TopicMastery.accuracy < 60.0
    )
    weak_topics = (await db.execute(weak_query)).scalars().all()
    
    # Get all topics for names
    topics = (await db.execute(select(Topic))).scalars().all()
    topic_map = {t.id: t.name for t in topics}

    context = {
        "due_revisions": [{"topic_id": r.topic_id, "topic_name": topic_map.get(r.topic_id, r.topic_id)} for r in due_revisions],
        "weak_topics": [{"topic_id": w.topic_id, "topic_name": topic_map.get(w.topic_id, w.topic_id), "accuracy": w.accuracy} for w in weak_topics]
    }
    return context

async def generate_study_plan_with_llm(db: AsyncSession, user_id: str, goal: str, duration_days: int, available_minutes: int):
    context = await generate_study_plan_context(db, user_id)
    
    prompt = f"""
    You are an AI Study Planner. Create a study plan for {duration_days} days, maximum {available_minutes} minutes per day.
    Goal: {goal}
    Student Context:
    Due Revisions: {json.dumps(context['due_revisions'])}
    Weak Topics: {json.dumps(context['weak_topics'])}
    
    Return a JSON response strictly matching this schema:
    {{
        "title": "Plan Title",
        "items": [
            {{
                "topic_id": "uuid or empty",
                "activity_type": "LEARN or PRACTICE or REVISION",
                "estimated_minutes": 15,
                "priority": "HIGH or MEDIUM"
            }}
        ]
    }}
    """
    
    if settings.LLM_API_KEY == "your_openai_api_key_here":
        # Mock for testing
        return {
            "title": "Mock Study Plan",
            "items": [
                {
                    "topic_id": context['weak_topics'][0]['topic_id'] if context['weak_topics'] else "",
                    "activity_type": "PRACTICE",
                    "estimated_minutes": 20,
                    "priority": "HIGH"
                }
            ]
        }

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
        return None
