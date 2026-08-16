from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func as sql_func
from ..models.personalization import LearningMemory
from ..models.learning import Mistake, TopicMastery, Topic


async def _get_topic_name(db: AsyncSession, topic_id: str) -> str:
    """Resolve topic_id to a human-readable topic name."""
    result = await db.execute(select(Topic.name).where(Topic.id == topic_id))
    name = result.scalar_one_or_none()
    return name or topic_id


async def _upsert_memory(
    db: AsyncSession,
    user_id: str,
    topic_id: str | None,
    memory_type: str,
    content: str,
    confidence: float,
    source: str
) -> LearningMemory:
    """Insert or update a learning memory. If a matching (user, topic, type) exists, update it."""
    filters = [
        LearningMemory.user_id == user_id,
        LearningMemory.memory_type == memory_type,
    ]
    if topic_id:
        filters.append(LearningMemory.topic_id == topic_id)
    else:
        filters.append(LearningMemory.topic_id.is_(None))

    result = await db.execute(select(LearningMemory).where(*filters))
    existing = result.scalar_one_or_none()

    if existing:
        existing.content = content
        existing.confidence = min(1.0, confidence)
        existing.source = source
        return existing
    else:
        mem = LearningMemory(
            user_id=user_id,
            memory_type=memory_type,
            topic_id=topic_id,
            content=content,
            confidence=min(1.0, confidence),
            source=source,
        )
        db.add(mem)
        return mem


async def evaluate_and_store_memory(db: AsyncSession, user_id: str, topic_id: str):
    """
    Analyze a student's performance on a topic and create/update learning memories.

    Evaluates:
    1. Weaknesses — low accuracy + multiple mistakes
    2. Strengths — high accuracy + sufficient attempts
    3. Misconceptions — repeated mistakes of the same type
    4. Achievements — mastery milestones reached
    5. Learning Patterns — common error categories
    """
    topic_name = await _get_topic_name(db, topic_id)

    # Retrieve topic mastery
    mastery_result = await db.execute(
        select(TopicMastery).where(
            TopicMastery.user_id == user_id,
            TopicMastery.topic_id == topic_id
        )
    )
    mastery = mastery_result.scalar_one_or_none()
    if not mastery:
        return

    # Retrieve recent mistakes for this topic (last 10)
    mistake_result = await db.execute(
        select(Mistake).where(
            Mistake.user_id == user_id,
            Mistake.topic_id == topic_id
        ).order_by(Mistake.created_at.desc()).limit(10)
    )
    recent_mistakes = mistake_result.scalars().all()

    # --- 1. WEAKNESS detection ---
    # Requires: accuracy < 50% AND at least 2 recent mistakes
    if mastery.accuracy < 50.0 and len(recent_mistakes) >= 2:
        await _upsert_memory(
            db, user_id, topic_id,
            memory_type="WEAKNESS",
            content=f"Student struggles with {topic_name}. "
                    f"Accuracy is {mastery.accuracy:.0f}% over {mastery.questions_attempted} attempts. "
                    f"Requires additional foundational practice.",
            confidence=0.8 + min(0.2, len(recent_mistakes) * 0.02),
            source="SYSTEM_EVALUATION"
        )
    else:
        # If accuracy improved, remove the weakness memory
        weak_result = await db.execute(
            select(LearningMemory).where(
                LearningMemory.user_id == user_id,
                LearningMemory.topic_id == topic_id,
                LearningMemory.memory_type == "WEAKNESS"
            )
        )
        weak_mem = weak_result.scalar_one_or_none()
        if weak_mem and mastery.accuracy >= 65.0:
            await db.delete(weak_mem)

    # --- 2. STRENGTH detection ---
    # Requires: accuracy > 85% AND at least 5 questions attempted
    if mastery.accuracy > 85.0 and mastery.questions_attempted >= 5:
        await _upsert_memory(
            db, user_id, topic_id,
            memory_type="STRENGTH",
            content=f"Student excels at {topic_name}. "
                    f"Accuracy is {mastery.accuracy:.0f}% over {mastery.questions_attempted} attempts. "
                    f"Can handle advanced difficulty.",
            confidence=0.8 + min(0.2, mastery.questions_attempted * 0.01),
            source="SYSTEM_EVALUATION"
        )

    # --- 3. MISCONCEPTION detection ---
    # Look for repeated error categories (same type appearing 3+ times)
    if len(recent_mistakes) >= 3:
        error_counts: dict[str, int] = {}
        for m in recent_mistakes:
            error_counts[m.error_category] = error_counts.get(m.error_category, 0) + 1

        for category, count in error_counts.items():
            if count >= 3 and category != "UNKNOWN":
                await _upsert_memory(
                    db, user_id, topic_id,
                    memory_type="MISCONCEPTION",
                    content=f"Student has a recurring {category.replace('_', ' ').lower()} "
                            f"pattern in {topic_name} ({count} occurrences). "
                            f"Targeted remediation recommended.",
                    confidence=min(1.0, 0.6 + count * 0.05),
                    source="MISTAKE_ANALYSIS"
                )

    # --- 4. ACHIEVEMENT detection ---
    # Milestones: first perfect accuracy on 5+ questions, mastery > 80
    if mastery.mastery_score >= 80.0 and mastery.questions_attempted >= 5:
        await _upsert_memory(
            db, user_id, topic_id,
            memory_type="ACHIEVEMENT",
            content=f"Student has achieved mastery in {topic_name} "
                    f"(score: {mastery.mastery_score:.0f}, accuracy: {mastery.accuracy:.0f}%).",
            confidence=1.0,
            source="SYSTEM_EVALUATION"
        )

    # --- 5. LEARNING_PATTERN detection ---
    # Analyze across all topics for common error patterns
    all_mistakes_result = await db.execute(
        select(Mistake.error_category, sql_func.count(Mistake.id).label("cnt"))
        .where(Mistake.user_id == user_id)
        .group_by(Mistake.error_category)
        .order_by(sql_func.count(Mistake.id).desc())
        .limit(3)
    )
    patterns = all_mistakes_result.all()
    if patterns and patterns[0][1] >= 5:
        top_category = patterns[0][0]
        top_count = patterns[0][1]
        await _upsert_memory(
            db, user_id, None,  # No specific topic — global pattern
            memory_type="LEARNING_PATTERN",
            content=f"Student's most common error type across all topics is "
                    f"{top_category.replace('_', ' ').lower()} ({top_count} occurrences). "
                    f"Consider focusing practice sessions on reducing this error type.",
            confidence=min(1.0, 0.6 + top_count * 0.03),
            source="PATTERN_ANALYSIS"
        )

    await db.commit()


async def get_memories(db: AsyncSession, user_id: str, topic_id: str | None = None, memory_type: str | None = None) -> list[LearningMemory]:
    """Retrieve learning memories for a user, optionally filtered by topic and type."""
    filters = [LearningMemory.user_id == user_id]
    if topic_id:
        filters.append(LearningMemory.topic_id == topic_id)
    if memory_type:
        filters.append(LearningMemory.memory_type == memory_type)

    result = await db.execute(
        select(LearningMemory)
        .where(*filters)
        .order_by(LearningMemory.updated_at.desc())
    )
    return result.scalars().all()
