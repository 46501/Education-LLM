from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc, func as sql_func
from ..models.learning import TopicMastery, Mistake, Topic
from ..models.personalization import RevisionSchedule, LearningMemory, TopicPrerequisite


class RecommendationEngine:
    """Original analytics-style recommendation engine used by /api/analytics/recommendations."""

    async def generate_recommendations(self, db: AsyncSession, user_id: str) -> list[str]:
        recommendations = []

        # Find weak topics
        stmt = (
            select(TopicMastery, Topic)
            .join(Topic, TopicMastery.topic_id == Topic.id)
            .where(TopicMastery.user_id == user_id)
            .order_by(TopicMastery.mastery_score)
        )
        result = await db.execute(stmt)
        mastery_records = result.all()

        for mastery, topic in mastery_records:
            if mastery.questions_attempted >= 3:
                if mastery.mastery_score < 40:
                    recommendations.append(f"Revise {topic.name} fundamentals. Your mastery is low.")
                    recommendations.append(f"Practice 5 easy questions on {topic.name}.")
                elif mastery.mastery_score < 70 and mastery.current_difficulty == "MEDIUM":
                    recommendations.append(f"You are ready for more medium-level questions in {topic.name}.")

            if mastery.mastery_score > 80:
                recommendations.append(f"Great job on {topic.name}! Try some expert-level challenges.")

        # Find common mistakes
        mistake_stmt = select(Mistake.error_category).where(Mistake.user_id == user_id)
        m_result = await db.execute(mistake_stmt)
        mistakes = m_result.scalars().all()

        if mistakes:
            category_counts: dict[str, int] = {}
            for m in mistakes:
                category_counts[m] = category_counts.get(m, 0) + 1

            most_common = max(category_counts, key=category_counts.get)
            if category_counts[most_common] > 2:
                if most_common == "CARELESS_ERROR":
                    recommendations.append("You have several careless errors. Take your time reading the questions!")
                elif most_common == "CONCEPTUAL_ERROR":
                    recommendations.append("You have multiple conceptual errors. Consider revisiting the core study materials or asking the AI Tutor to explain the concepts.")

        if not recommendations:
            recommendations.append("Keep practicing! Start a new quiz to generate personalized recommendations.")

        return list(set(recommendations))  # Deduplicate


recommendation_engine = RecommendationEngine()


async def get_personalized_recommendations(db: AsyncSession, user_id: str) -> list[dict]:
    """
    Generate ranked, actionable personalization recommendations.

    Sources:
    1. Due revisions (highest priority)
    2. Weak topics (accuracy < 60%)
    3. Unmet prerequisites
    4. Difficulty advancement suggestions
    5. Misconception-targeted practice
    """
    recommendations = []
    priority_order = 0

    # Build topic name map
    topics = (await db.execute(select(Topic))).scalars().all()
    topic_map = {t.id: t.name for t in topics}

    # --- 1. Due Revisions ---
    rev_query = select(RevisionSchedule).where(
        RevisionSchedule.user_id == user_id,
        RevisionSchedule.status == "DUE"
    ).order_by(RevisionSchedule.next_review)
    due_revisions = (await db.execute(rev_query)).scalars().all()

    for rev in due_revisions:
        topic_name = topic_map.get(rev.topic_id, rev.topic_id)
        priority_order += 1
        recommendations.append({
            "type": "REVISION",
            "topic": topic_name,
            "priority": "HIGH",
            "reason": f"Topic '{topic_name}' is overdue for revision.",
            "action": f"Complete a revision quiz for {topic_name}."
        })

    # --- 2. Weak Topics ---
    weak_query = (
        select(TopicMastery)
        .where(TopicMastery.user_id == user_id, TopicMastery.accuracy < 60.0)
        .order_by(TopicMastery.accuracy)
    )
    weak_topics = (await db.execute(weak_query)).scalars().all()

    for weak in weak_topics:
        topic_name = topic_map.get(weak.topic_id, weak.topic_id)
        recommendations.append({
            "type": "PRACTICE",
            "topic": topic_name,
            "priority": "HIGH",
            "reason": f"Your accuracy in {topic_name} is {weak.accuracy:.0f}%.",
            "action": f"Practice {topic_name} to improve your mastery."
        })

    # --- 3. Unmet Prerequisites ---
    prereq_query = select(TopicPrerequisite)
    all_prereqs = (await db.execute(prereq_query)).scalars().all()

    # Get mastery for this user
    mastery_query = select(TopicMastery).where(TopicMastery.user_id == user_id)
    all_mastery = (await db.execute(mastery_query)).scalars().all()
    mastery_map = {m.topic_id: m for m in all_mastery}

    for prereq in all_prereqs:
        # If user has attempted the topic but not the prerequisite, or prereq mastery is low
        if prereq.topic_id in mastery_map:
            prereq_mastery = mastery_map.get(prereq.prerequisite_topic_id)
            prereq_name = topic_map.get(prereq.prerequisite_topic_id, prereq.prerequisite_topic_id)
            topic_name = topic_map.get(prereq.topic_id, prereq.topic_id)

            if not prereq_mastery or prereq_mastery.mastery_score < 50:
                recommendations.append({
                    "type": "PREREQUISITE",
                    "topic": prereq_name,
                    "priority": "HIGH",
                    "reason": f"'{prereq_name}' is a prerequisite for '{topic_name}' and needs improvement.",
                    "action": f"Study and practice {prereq_name} before continuing with {topic_name}."
                })

    # --- 4. Difficulty Advancement ---
    for mastery_record in all_mastery:
        if mastery_record.mastery_score >= 70 and mastery_record.current_difficulty in ("BEGINNER", "EASY", "MEDIUM"):
            topic_name = topic_map.get(mastery_record.topic_id, mastery_record.topic_id)
            next_diff = {
                "BEGINNER": "EASY", "EASY": "MEDIUM", "MEDIUM": "HARD"
            }.get(mastery_record.current_difficulty, mastery_record.current_difficulty)
            recommendations.append({
                "type": "ADVANCEMENT",
                "topic": topic_name,
                "priority": "MEDIUM",
                "reason": f"Your mastery in {topic_name} is {mastery_record.mastery_score:.0f}%. Ready for harder questions.",
                "action": f"Try {next_diff.lower()}-level questions in {topic_name}."
            })

    # --- 5. Misconception-targeted practice ---
    misconception_query = select(LearningMemory).where(
        LearningMemory.user_id == user_id,
        LearningMemory.memory_type == "MISCONCEPTION"
    )
    misconceptions = (await db.execute(misconception_query)).scalars().all()

    for mc in misconceptions:
        topic_name = topic_map.get(mc.topic_id, mc.topic_id) if mc.topic_id else "General"
        recommendations.append({
            "type": "MISCONCEPTION",
            "topic": topic_name,
            "priority": "MEDIUM",
            "reason": mc.content,
            "action": f"Ask the AI Tutor to explain the concepts related to your errors in {topic_name}."
        })

    # Default if empty
    if not recommendations:
        recommendations.append({
            "type": "GENERAL",
            "topic": "All topics",
            "priority": "LOW",
            "reason": "No specific issues detected.",
            "action": "Keep practicing! Start a new quiz to generate personalized recommendations."
        })

    return recommendations


async def get_learning_path(db: AsyncSession, user_id: str) -> list[dict]:
    """
    Generate a learning path — an ordered list of topics from weakest to strongest,
    showing mastery status, recommended action, and prerequisite dependencies.
    """
    topics = (await db.execute(select(Topic))).scalars().all()
    topic_map = {t.id: t for t in topics}

    mastery_query = select(TopicMastery).where(TopicMastery.user_id == user_id).order_by(TopicMastery.mastery_score)
    all_mastery = (await db.execute(mastery_query)).scalars().all()

    prereq_query = select(TopicPrerequisite)
    all_prereqs = (await db.execute(prereq_query)).scalars().all()
    prereq_map: dict[str, list[str]] = {}
    for p in all_prereqs:
        prereq_map.setdefault(p.topic_id, []).append(p.prerequisite_topic_id)

    path = []
    for mastery_record in all_mastery:
        topic = topic_map.get(mastery_record.topic_id)
        if not topic:
            continue

        # Determine status
        if mastery_record.mastery_score >= 80:
            status = "MASTERED"
        elif mastery_record.mastery_score >= 50:
            status = "IN_PROGRESS"
        else:
            status = "NEEDS_WORK"

        # Get prerequisites
        prereqs = prereq_map.get(mastery_record.topic_id, [])
        prereq_names = [topic_map[pid].name for pid in prereqs if pid in topic_map]

        path.append({
            "topic_id": mastery_record.topic_id,
            "topic_name": topic.name,
            "mastery_score": mastery_record.mastery_score,
            "accuracy": mastery_record.accuracy,
            "current_difficulty": mastery_record.current_difficulty,
            "status": status,
            "prerequisites": prereq_names,
            "questions_attempted": mastery_record.questions_attempted,
        })

    return path
