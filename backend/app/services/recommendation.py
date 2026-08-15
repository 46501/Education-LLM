from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from ..models.learning import TopicMastery, Mistake, Topic

class RecommendationEngine:
    async def generate_recommendations(self, db: AsyncSession, user_id: str) -> list[str]:
        recommendations = []

        # Find weak topics
        stmt = select(TopicMastery, Topic).join(Topic, TopicMastery.topic_id == Topic.id).where(
            TopicMastery.user_id == user_id
        ).order_by(TopicMastery.mastery_score)
        
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
            # Count categories
            category_counts = {}
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

        return list(set(recommendations)) # Deduplicate

recommendation_engine = RecommendationEngine()
