from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.learning import TopicMastery

class ScoringEngine:
    DIFFICULTY_WEIGHTS = {
        "BEGINNER": 0.4,
        "EASY": 0.6,
        "MEDIUM": 0.8,
        "HARD": 1.0,
        "EXPERT": 1.2
    }
    
    # Caps to prevent someone mastering a topic just by doing easy questions
    DIFFICULTY_CAPS = {
        "BEGINNER": 40.0,
        "EASY": 60.0,
        "MEDIUM": 80.0,
        "HARD": 100.0,
        "EXPERT": 100.0
    }

    async def update_mastery(self, db: AsyncSession, user_id: str, topic_id: str, is_correct: bool, difficulty: str):
        result = await db.execute(select(TopicMastery).where(TopicMastery.user_id == user_id, TopicMastery.topic_id == topic_id))
        mastery = result.scalars().first()

        if not mastery:
            mastery = TopicMastery(user_id=user_id, topic_id=topic_id)
            db.add(mastery)

        mastery.questions_attempted += 1
        if is_correct:
            mastery.questions_correct += 1
        else:
            mastery.questions_incorrect += 1
        
        mastery.accuracy = (mastery.questions_correct / mastery.questions_attempted) * 100

        # Calculate new mastery score
        base_score = mastery.accuracy
        weight = self.DIFFICULTY_WEIGHTS.get(difficulty, 0.5)
        cap = self.DIFFICULTY_CAPS.get(difficulty, 50.0)

        # Exponential moving average style to heavily weight recent performance
        # but since we only have aggregate stats right now, we use a heuristic:
        calculated_score = base_score * weight
        
        # Apply cap
        if calculated_score > cap:
            calculated_score = cap

        # Only increase mastery if they got it right, otherwise decrease it slightly more than just accuracy drop
        if is_correct:
            mastery.mastery_score = min(cap, max(mastery.mastery_score, calculated_score))
        else:
            mastery.mastery_score = max(0.0, mastery.mastery_score - (10.0 / weight))

        # Adjust current recommended difficulty
        if mastery.mastery_score > 80:
            mastery.current_difficulty = "EXPERT"
        elif mastery.mastery_score > 60:
            mastery.current_difficulty = "HARD"
        elif mastery.mastery_score > 40:
            mastery.current_difficulty = "MEDIUM"
        elif mastery.mastery_score > 20:
            mastery.current_difficulty = "EASY"
        else:
            mastery.current_difficulty = "BEGINNER"

        await db.commit()
        await db.refresh(mastery)
        return mastery

scoring_engine = ScoringEngine()
