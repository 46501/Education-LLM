from pydantic import BaseModel, Field
from typing import List

class AnswerEvaluationResponse(BaseModel):
    score: float = Field(..., description="A score between 0.0 and 1.0 representing the correctness.")
    is_correct: bool = Field(..., description="True if the answer is conceptually correct (score >= 0.8), False otherwise.")
    strengths: List[str] = Field(..., description="List of conceptually correct points the student made.")
    mistakes: List[str] = Field(..., description="List of mistakes or misconceptions in the student's answer.")
    missing_points: List[str] = Field(..., description="List of key points the student missed compared to the expected answer.")
    feedback: str = Field(..., description="Constructive, encouraging feedback explaining the evaluation to the student.")

ANSWER_EVALUATION_PROMPT = """
You are an expert AI tutor evaluating a student's short answer.
Topic: {topic}
Question: {question}
Expected Correct Answer: {correct_answer}
Student Answer: {student_answer}

Evaluate the student's answer based on conceptual correctness, relevance, and completeness.
IMPORTANT RULES:
1. Do not penalize the student for using different wording or synonyms. Focus purely on meaning.
2. If the student demonstrates clear understanding of the core concept, they should receive a high score even if it's brief.
3. Be encouraging in your feedback.
"""
