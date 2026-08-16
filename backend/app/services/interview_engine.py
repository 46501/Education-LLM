from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func
import json
import logging
from datetime import datetime, timezone

from ..models.interview import Interview, InterviewSession, InterviewMessage
from ..prompts.interview_engine import INTERVIEW_TURN_PROMPT, INTERVIEW_COMPLETION_PROMPT
from ..core.config import settings
from litellm import acompletion

logger = logging.getLogger(__name__)

class InterviewEngine:
    def __init__(self):
        self.model = "gpt-4o-mini"
        
    async def process_answer(self, db: AsyncSession, session_id: str, user_id: str, answer_text: str):
        # 1. Fetch Session and Messages
        result = await db.execute(
            select(InterviewSession)
            .options(selectinload(InterviewSession.messages), selectinload(InterviewSession.interview))
            .where(InterviewSession.id == session_id, InterviewSession.user_id == user_id)
        )
        session = result.scalars().first()
        
        if not session or session.status != "IN_PROGRESS":
            raise ValueError("Invalid session or not in progress")
            
        interview = session.interview
        
        # 2. Record the student's answer
        student_msg = InterviewMessage(
            session_id=session.id,
            role="student",
            content=answer_text
        )
        db.add(student_msg)
        await db.flush() # flush to get id and timestamp
        
        # 3. Construct history for LLM
        # We need the AI to read history, evaluate the last answer, and pose the next question
        chat_history = []
        for msg in session.messages:
            chat_history.append({"role": "user" if msg.role == "student" else "assistant", "content": msg.content})
            
        chat_history.append({"role": "user", "content": answer_text})
        
        prompt = INTERVIEW_TURN_PROMPT.format(
            role=interview.role,
            level=interview.experience_level,
            topics=", ".join(interview.topics) if interview.topics else "General"
        )
        
        try:
            if not settings.LLM_API_KEY or settings.LLM_API_KEY == "your_openai_api_key_here":
                eval_data = {
                    "score": 8.0,
                    "technical_accuracy": 8.0,
                    "depth": 7.5,
                    "clarity": 9.0,
                    "missing_points": ["Mock missing point"],
                    "feedback": "Mock evaluation feedback"
                }
                next_q = "Mock next question based on your answer."
            else:
                response = await acompletion(
                    model=self.model,
                    messages=[{"role": "system", "content": prompt}] + chat_history,
                    response_format={"type": "json_object"}
                )
                raw = response.choices[0].message.content
                parsed = json.loads(raw)
                eval_data = parsed.get("evaluation", {})
                next_q = parsed.get("next_question", "Thank you, what else can you tell me?")
                
            # Update student message with evaluation
            student_msg.evaluation = eval_data
            
            # Record next question
            ai_msg = InterviewMessage(
                session_id=session.id,
                role="interviewer",
                content=next_q
            )
            db.add(ai_msg)
            
            await db.commit()
            return {"evaluation": eval_data, "next_question": next_q}
            
        except Exception as e:
            logger.error(f"Interview engine error: {e}")
            await db.rollback()
            raise e

    async def complete_interview(self, db: AsyncSession, session_id: str, user_id: str):
        result = await db.execute(
            select(InterviewSession)
            .options(selectinload(InterviewSession.messages), selectinload(InterviewSession.interview))
            .where(InterviewSession.id == session_id, InterviewSession.user_id == user_id)
        )
        session = result.scalars().first()
        
        if not session or session.status == "COMPLETED":
            return session
            
        session.status = "COMPLETED"
        session.completed_at = datetime.now(timezone.utc)
        
        # Calculate summary evaluation
        chat_history = []
        avg_score = 0
        count = 0
        for msg in session.messages:
            chat_history.append({"role": "user" if msg.role == "student" else "assistant", "content": msg.content})
            if msg.role == "student" and msg.evaluation:
                avg_score += msg.evaluation.get("score", 0)
                count += 1
                
        final_score = (avg_score / count) if count > 0 else 0
        session.score = final_score
        
        try:
            if not settings.LLM_API_KEY or settings.LLM_API_KEY == "your_openai_api_key_here":
                session.feedback = {
                    "strengths": ["Mock strength"],
                    "weaknesses": ["Mock weakness"],
                    "frequently_missed_concepts": ["Mock missed concept"],
                    "communication_feedback": "Mock comms feedback",
                    "technical_recommendations": "Mock recs",
                    "recommended_practice": "Mock practice"
                }
            else:
                response = await acompletion(
                    model=self.model,
                    messages=[{"role": "system", "content": INTERVIEW_COMPLETION_PROMPT}] + chat_history,
                    response_format={"type": "json_object"}
                )
                raw = response.choices[0].message.content
                parsed = json.loads(raw)
                session.feedback = parsed
                if "overall_score" in parsed:
                    session.score = parsed["overall_score"]
        except Exception as e:
            logger.error(f"Failed to generate final interview feedback: {e}")
            
        await db.commit()
        return session

interview_engine = InterviewEngine()
