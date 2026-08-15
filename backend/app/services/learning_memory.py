from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.personalization import LearningMemory
from ..models.learning import Mistake, TopicMastery

async def evaluate_and_store_memory(db: AsyncSession, user_id: str, topic_id: str):
    # Retrieve recent mistakes for the topic
    mistake_query = select(Mistake).where(
        Mistake.user_id == user_id,
        Mistake.topic_id == topic_id
    ).order_by(Mistake.created_at.desc()).limit(3)
    mistakes = (await db.execute(mistake_query)).scalars().all()

    # Retrieve topic mastery
    mastery_query = select(TopicMastery).where(
        TopicMastery.user_id == user_id,
        TopicMastery.topic_id == topic_id
    )
    mastery = (await db.execute(mastery_query)).scalar_one_or_none()

    if not mastery:
        return

    # Check if student is struggling (accuracy < 50% and multiple mistakes)
    if mastery.accuracy < 50.0 and len(mistakes) >= 2:
        # Check if a weakness memory already exists
        mem_query = select(LearningMemory).where(
            LearningMemory.user_id == user_id,
            LearningMemory.topic_id == topic_id,
            LearningMemory.memory_type == "WEAKNESS"
        )
        existing_mem = (await db.execute(mem_query)).scalar_one_or_none()

        if existing_mem:
            existing_mem.confidence = min(1.0, existing_mem.confidence + 0.1)
        else:
            new_mem = LearningMemory(
                user_id=user_id,
                memory_type="WEAKNESS",
                topic_id=topic_id,
                content=f"Student struggles with {topic_id} concepts. Requires additional foundational practice.",
                confidence=0.8,
                source="SYSTEM_EVALUATION"
            )
            db.add(new_mem)

    # Check if student is excelling (accuracy > 85% and attempted >= 5 questions)
    elif mastery.accuracy > 85.0 and mastery.questions_attempted >= 5:
        mem_query = select(LearningMemory).where(
            LearningMemory.user_id == user_id,
            LearningMemory.topic_id == topic_id,
            LearningMemory.memory_type == "STRENGTH"
        )
        existing_mem = (await db.execute(mem_query)).scalar_one_or_none()

        if existing_mem:
            existing_mem.confidence = min(1.0, existing_mem.confidence + 0.1)
        else:
            new_mem = LearningMemory(
                user_id=user_id,
                memory_type="STRENGTH",
                topic_id=topic_id,
                content=f"Student excels at {topic_id}. Can handle advanced difficulty.",
                confidence=0.8,
                source="SYSTEM_EVALUATION"
            )
            db.add(new_mem)
            
            # Invalidate weaknesses if they existed
            weak_query = select(LearningMemory).where(
                LearningMemory.user_id == user_id,
                LearningMemory.topic_id == topic_id,
                LearningMemory.memory_type == "WEAKNESS"
            )
            weak_mem = (await db.execute(weak_query)).scalar_one_or_none()
            if weak_mem:
                db.delete(weak_mem)

    await db.commit()
