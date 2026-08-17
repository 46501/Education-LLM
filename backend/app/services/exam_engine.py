from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func
import json
import logging
from datetime import datetime, timezone

from ..models.exam import Exam, ExamTopic, ExamQuestion, ExamSession
from ..models.learning import Question, Topic, QuestionAttempt, TopicMastery, Mistake
from ..models.personalization import LearningMemory
from ..prompts.exam_generation import EXAM_GENERATION_PROMPT, ExamGenerationResponse
from ..core.config import settings
from .rag import rag_service
from .llm import safe_acompletion
from .evaluator import answer_evaluator
from .scoring import scoring_engine

logger = logging.getLogger(__name__)

class ExamEngine:
    def __init__(self):
        self.model = "gpt-4o-mini"
    
    async def calculate_readiness(self, db: AsyncSession, user_id: str, exam_id: str) -> float:
        # Deterministic Exam Readiness Score
        # Fetches ExamTopics, averages topic mastery, applies penalties for overdue revisions
        exam = await db.get(Exam, exam_id)
        if not exam:
            return 0.0
        
        result = await db.execute(select(ExamTopic).where(ExamTopic.exam_id == exam_id))
        exam_topics = result.scalars().all()
        
        if not exam_topics:
            return 0.0
            
        total_mastery = 0.0
        total_weight = 0.0
        
        for et in exam_topics:
            mastery_res = await db.execute(select(TopicMastery).where(TopicMastery.user_id == user_id, TopicMastery.topic_id == et.topic_id))
            mastery = mastery_res.scalars().first()
            score = mastery.mastery_score if mastery else 0.0
            total_mastery += score * et.weight
            total_weight += et.weight
            
        if total_weight == 0:
            return 0.0
            
        base_readiness = total_mastery / total_weight
        return min(max(base_readiness, 0.0), 100.0)

    async def generate_mock_exam(self, db: AsyncSession, exam_id: str, user_id: str):
        # 1. Fetch Exam details and Topics
        result = await db.execute(select(Exam).options(selectinload(Exam.topics).selectinload(ExamTopic.topic)).where(Exam.id == exam_id, Exam.user_id == user_id))
        exam = result.scalars().first()
        
        if not exam:
            raise ValueError("Exam not found or unauthorized")
            
        # Target question count based on duration and marks (heuristic: 1 mark per question for mock if not specified)
        target_questions = int(exam.total_marks)
        
        # Determine how many questions per topic based on weight
        total_weight = sum([et.weight for et in exam.topics])
        if total_weight == 0:
            return exam
            
        existing_questions_to_link = []
        new_questions_to_create = []
        
        for et in exam.topics:
            q_count = max(1, int((et.weight / total_weight) * target_questions))
            
            # 1. Try to pull existing questions for this topic
            q_res = await db.execute(
                select(Question)
                .where(Question.topic_id == et.topic_id)
                .order_by(func.random())
                .limit(q_count)
            )
            found_questions = q_res.scalars().all()
            existing_questions_to_link.extend(found_questions)
            
            # 2. If short, generate via LLM
            shortfall = q_count - len(found_questions)
            if shortfall > 0:
                logger.info(f"Generating {shortfall} fallback questions for topic {et.topic.name}")
                context = await self._get_rag_context(db, user_id, et.topic.name)
                prompt = EXAM_GENERATION_PROMPT.format(
                    num_questions=shortfall,
                    topic=et.topic.name,
                    difficulty="MEDIUM", # Or derive from preference
                    context=context
                )
                
                try:
                    if not settings.LLM_API_KEY or settings.LLM_API_KEY == "your_openai_api_key_here":
                        # Mock generation
                        for i in range(shortfall):
                            q = Question(
                                subject_id=et.topic.subject_id,
                                topic_id=et.topic.id,
                                question_text=f"Mock generated question {i} for {et.topic.name}",
                                question_type="SHORT_ANSWER",
                                difficulty="MEDIUM",
                                correct_answer="Mock answer",
                                explanation="Mock explanation"
                            )
                            db.add(q)
                            new_questions_to_create.append((q, 1.0))
                    else:
                        response = await safe_acompletion(
                            model=self.model,
                            messages=[{"role": "user", "content": prompt}],
                            response_format={"type": "json_object"}
                        )
                        raw_content = response.choices[0].message.content
                        if not raw_content:
                            continue
                            
                        # Parse standard JSON instead of relying on instructor/structured output due to environment restrictions
                        # (Assuming LiteLLM json_object format handles it)
                        parsed = json.loads(raw_content)
                        # Manual mapping
                        if "questions" in parsed:
                            for q_data in parsed["questions"]:
                                q = Question(
                                    subject_id=et.topic.subject_id,
                                    topic_id=et.topic.id,
                                    question_text=q_data.get("question_text", ""),
                                    question_type=q_data.get("question_type", "SHORT_ANSWER"),
                                    difficulty=q_data.get("difficulty", "MEDIUM"),
                                    options=q_data.get("options", None),
                                    correct_answer=q_data.get("correct_answer", ""),
                                    explanation=q_data.get("explanation", "")
                                )
                                db.add(q)
                                new_questions_to_create.append((q, q_data.get("marks", 1.0)))
                except Exception as e:
                    logger.error(f"Failed to generate exam questions: {e}")
                    
        await db.flush() # Ensure new questions have IDs
        
        # Link all questions to Exam
        all_q = [(q, 1.0) for q in existing_questions_to_link] + new_questions_to_create
        
        # Clear existing links if re-generating
        await db.execute(ExamQuestion.__table__.delete().where(ExamQuestion.exam_id == exam_id))
        
        for idx, (q, marks) in enumerate(all_q):
            eq = ExamQuestion(
                exam_id=exam_id,
                question_id=q.id,
                question_order=idx + 1,
                marks=marks
            )
            db.add(eq)
            
        await db.commit()
        return exam

    async def _get_rag_context(self, db, user_id, topic_name):
        rag_results = await rag_service.retrieve_context(db, user_id, topic_name, top_k=5)
        if rag_results:
            return "\n".join([f"Source [{r['filename']}]: {r['content']}" for r in rag_results])
        return "No additional context found."

    async def evaluate_exam(self, db: AsyncSession, session_id: str, user_id: str, answers: list):
        # 1. Fetch Session and Exam
        result = await db.execute(select(ExamSession).where(ExamSession.id == session_id, ExamSession.user_id == user_id))
        session = result.scalars().first()
        
        if not session or session.status in ["SUBMITTED", "EXPIRED"]:
            raise ValueError("Invalid session or already submitted")
            
        # 2. Lock session
        session.status = "SUBMITTED"
        session.submitted_at = datetime.now(timezone.utc)
        
        if session.started_at:
            session.duration = int((session.submitted_at - session.started_at).total_seconds())
            
        total_score = 0.0
        
        # 3. Evaluate each answer
        for ans in answers:
            question_id = ans.get("question_id")
            user_answer = ans.get("answer")
            
            # Fetch ExamQuestion to get marks
            eq_res = await db.execute(select(ExamQuestion).where(ExamQuestion.exam_id == session.exam_id, ExamQuestion.question_id == question_id))
            eq = eq_res.scalars().first()
            if not eq:
                continue
                
            q_res = await db.execute(select(Question).where(Question.id == question_id))
            question = q_res.scalars().first()
            
            if not question:
                continue
                
            # Evaluate using existing answer_evaluator
            eval_result = await answer_evaluator.evaluate_answer(
                question.question_type,
                question.correct_answer,
                user_answer
            )
            
            is_correct = eval_result["is_correct"]
            score = (eval_result["score"] / 10.0) * eq.marks if not is_correct else eq.marks
            total_score += score
            
            # Record Attempt
            attempt = QuestionAttempt(
                user_id=user_id,
                exam_id=session.exam_id,
                question_id=question_id,
                submitted_answer=user_answer,
                is_correct=is_correct,
                score=score,
                max_score=eq.marks,
                evaluation_feedback=eval_result
            )
            db.add(attempt)
            
            # Update Mastery
            await scoring_engine.update_mastery(db, user_id, question.topic_id, is_correct, eval_result["score"])
            
            # Record Mistake if wrong
            if not is_correct:
                mistake_cat = await answer_evaluator.classify_mistake(question.question_text, question.correct_answer, user_answer)
                mistake = Mistake(
                    user_id=user_id,
                    topic_id=question.topic_id,
                    question_id=question_id,
                    error_category=mistake_cat,
                    student_answer=user_answer,
                    explanation=eval_result.get("feedback", "")
                )
                db.add(mistake)
                
                # Update Learning Memory
                mem = LearningMemory(
                    user_id=user_id,
                    memory_type="WEAKNESS",
                    topic_id=question.topic_id,
                    content=f"Exam mistake in {mistake_cat} for topic.",
                    source="EXAM_ATTEMPT"
                )
                db.add(mem)
                
        session.score = total_score
        await db.commit()
        return session

exam_engine = ExamEngine()
