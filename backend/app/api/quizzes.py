from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from pydantic import BaseModel

from ..core.database import get_db
from ..models.user import User
from ..models.learning import Quiz, QuizQuestion, Question, QuestionAttempt, Subject, Topic
from ..services.quiz_generator import quiz_generator
import logging

logger = logging.getLogger(__name__)
from ..services.evaluator import answer_evaluator
from ..services.scoring import scoring_engine
from .deps import get_current_user
import uuid

router = APIRouter()

class GenerateQuizRequest(BaseModel):
    title: str
    subject: str
    topic: str
    difficulty: str
    number_of_questions: int
    question_type: str = "MCQ"
    use_rag: bool = False

class SubmitAnswerRequest(BaseModel):
    question_id: str
    submitted_answer: str

class SubmitQuizRequest(BaseModel):
    answers: List[SubmitAnswerRequest]

@router.post("/generate")
async def generate_quiz(req: GenerateQuizRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # Create Subject / Topic if they don't exist
    result = await db.execute(select(Subject).where(Subject.name == req.subject))
    subj = result.scalars().first()
    if not subj:
        subj = Subject(name=req.subject)
        db.add(subj)
        await db.flush()

    result = await db.execute(select(Topic).where(Topic.name == req.topic, Topic.subject_id == subj.id))
    topic = result.scalars().first()
    if not topic:
        topic = Topic(name=req.topic, subject_id=subj.id)
        db.add(topic)
        await db.flush()

    # Call LLM Generator
    generation_response = await quiz_generator.generate_questions(
        db=db,
        user_id=current_user.id,
        subject=req.subject,
        topic=req.topic,
        difficulty=req.difficulty,
        num_questions=req.number_of_questions,
        question_type=req.question_type,
        use_rag=req.use_rag
    )

    # Save Quiz
    quiz = Quiz(
        user_id=current_user.id,
        title=req.title,
        subject_id=subj.id,
        topic_id=topic.id,
        difficulty=req.difficulty,
        number_of_questions=req.number_of_questions,
        status="CREATED"
    )
    db.add(quiz)
    await db.flush()

    # Save Questions and QuizQuestions
    for idx, q_data in enumerate(generation_response.questions):
        question = Question(
            subject_id=subj.id,
            topic_id=topic.id,
            question_text=q_data.question_text,
            question_type=req.question_type,
            difficulty=q_data.difficulty,
            options=q_data.options,
            correct_answer=q_data.correct_answer,
            explanation=q_data.explanation
        )
        db.add(question)
        await db.flush()

        qq = QuizQuestion(
            quiz_id=quiz.id,
            question_id=question.id,
            question_order=idx + 1
        )
        db.add(qq)

    await db.commit()
    return {"quiz_id": quiz.id, "message": "Quiz generated successfully"}

@router.get("/{quiz_id}")
async def get_quiz(quiz_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Quiz).options(selectinload(Quiz.questions).selectinload(QuizQuestion.question))
        .where(Quiz.id == quiz_id, Quiz.user_id == current_user.id)
    )
    quiz = result.scalars().first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Hide answers
    questions = []
    for qq in sorted(quiz.questions, key=lambda x: x.question_order):
        q = qq.question
        questions.append({
            "id": q.id,
            "text": q.question_text,
            "options": q.options,
            "type": q.question_type,
            "order": qq.question_order
        })

    return {
        "id": quiz.id,
        "title": quiz.title,
        "status": quiz.status,
        "questions": questions
    }

@router.post("/{quiz_id}/submit")
async def submit_quiz(quiz_id: str, req: SubmitQuizRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Quiz).options(selectinload(Quiz.questions).selectinload(QuizQuestion.question))
        .where(Quiz.id == quiz_id, Quiz.user_id == current_user.id)
    )
    quiz = result.scalars().first()
    if not quiz or quiz.status == "COMPLETED":
        raise HTTPException(status_code=400, detail="Quiz not found or already completed")

    # Map request answers
    answer_map = {ans.question_id: ans.submitted_answer for ans in req.answers}

    for qq in quiz.questions:
        q = qq.question
        sub_ans = answer_map.get(q.id)

        if not sub_ans:
            continue

        # Evaluate
        if q.question_type == "MCQ":
            eval_res = answer_evaluator.evaluate_mcq(sub_ans, q.correct_answer)
        elif q.question_type == "NUMERICAL":
            eval_res = answer_evaluator.evaluate_numerical(sub_ans, q.correct_answer)
        elif q.question_type == "SHORT_ANSWER":
            eval_res = await answer_evaluator.evaluate_short_answer(quiz.title, q.question_text, q.correct_answer, sub_ans)
        else:
            eval_res = {"score": 0.0, "is_correct": False, "feedback": "Unsupported type", "mistakes": []}

        attempt = QuestionAttempt(
            user_id=current_user.id,
            quiz_id=quiz.id,
            question_id=q.id,
            submitted_answer=sub_ans,
            is_correct=eval_res["is_correct"],
            score=eval_res["score"],
            evaluation_feedback=eval_res
        )
        db.add(attempt)

        # Update topic mastery
        await scoring_engine.update_mastery(db, current_user.id, q.topic_id, eval_res["is_correct"], q.difficulty)

        # Classify and log mistake if wrong
        if not eval_res["is_correct"]:
            from ..models.learning import Mistake
            mistake_res = await answer_evaluator.classify_mistake(quiz.title, q.question_text, q.correct_answer, sub_ans)
            mistake = Mistake(
                user_id=current_user.id,
                topic_id=q.topic_id,
                question_id=q.id,
                error_category=mistake_res.get("category", "UNKNOWN"),
                student_answer=sub_ans,
                explanation=mistake_res.get("explanation", "Failed to classify.")
            )
            db.add(mistake)

    import datetime
    quiz.status = "COMPLETED"
    quiz.completed_at = datetime.datetime.utcnow()
    await db.commit()

    # --- Phase 4 Personalization Integration ---
    try:
        from ..services.spaced_repetition import update_revision_schedule
        from ..services.learning_memory import evaluate_and_store_memory
        from ..services.streak import update_streak

        # Collect per-topic accuracy from this quiz
        topic_results: dict[str, dict] = {}
        for qq in quiz.questions:
            q = qq.question
            attempt_answer = answer_map.get(q.id)
            if not attempt_answer:
                continue
            if q.topic_id not in topic_results:
                topic_results[q.topic_id] = {"correct": 0, "total": 0}
            topic_results[q.topic_id]["total"] += 1
            # Re-check correctness from the attempt we already stored
            result_check = await db.execute(
                select(QuestionAttempt).where(
                    QuestionAttempt.quiz_id == quiz.id,
                    QuestionAttempt.question_id == q.id,
                    QuestionAttempt.user_id == current_user.id
                )
            )
            attempt_record = result_check.scalars().first()
            if attempt_record and attempt_record.is_correct:
                topic_results[q.topic_id]["correct"] += 1

        for tid, stats in topic_results.items():
            accuracy = (stats["correct"] / stats["total"]) * 100 if stats["total"] > 0 else 0
            await update_revision_schedule(db, current_user.id, tid, accuracy)
            await evaluate_and_store_memory(db, current_user.id, tid)

        # Update streak — quiz completion is a meaningful learning activity
        await update_streak(db, current_user.id)
    except Exception as e:
        logger.error(f"Phase 4 post-quiz integration error (non-fatal): {e}")

    return {"message": "Quiz evaluated and submitted successfully."}

@router.get("/{quiz_id}/results")
async def get_quiz_results(quiz_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(QuestionAttempt).options(selectinload(QuestionAttempt.question))
        .where(QuestionAttempt.quiz_id == quiz_id, QuestionAttempt.user_id == current_user.id)
    )
    attempts = result.scalars().all()
    
    total_score = sum(a.score for a in attempts)
    total_questions = len(attempts)

    breakdown = []
    for a in attempts:
        breakdown.append({
            "question": a.question.question_text,
            "submitted_answer": a.submitted_answer,
            "correct_answer": a.question.correct_answer,
            "is_correct": a.is_correct,
            "score": a.score,
            "feedback": a.evaluation_feedback
        })

    return {
        "total_score": total_score,
        "max_score": total_questions,
        "accuracy": (total_score / total_questions * 100) if total_questions > 0 else 0,
        "breakdown": breakdown
    }
