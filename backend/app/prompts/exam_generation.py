from pydantic import BaseModel, Field
from typing import List, Union, Optional

class ExamQuestionSchema(BaseModel):
    question_text: str = Field(..., description="The generated question text.")
    question_type: str = Field(..., description="MCQ, MULTIPLE_CORRECT, TRUE_FALSE, SHORT_ANSWER, NUMERICAL")
    options: Optional[List[str]] = Field(None, description="A list of 4 options if the question type is MCQ. Null otherwise.")
    correct_answer: Union[str, List[str], float] = Field(..., description="The correct answer. String for MCQ/Short Answer, list for multiple correct, float for numerical.")
    explanation: str = Field(..., description="A detailed explanation of why the answer is correct.")
    difficulty: str = Field(..., description="The difficulty level of the question: BEGINNER, EASY, MEDIUM, HARD, EXPERT")
    marks: float = Field(..., description="The marks awarded for this question.")

class ExamGenerationResponse(BaseModel):
    questions: List[ExamQuestionSchema] = Field(..., description="The generated list of exam questions.")

EXAM_GENERATION_PROMPT = """
You are an expert examiner. Your task is to generate {num_questions} questions for a mock exam.
The topic for these questions is "{topic}".
The target difficulty is {difficulty}.

Context:
{context}

Ensure that:
1. The questions strictly evaluate the topic.
2. For MCQs, provide exactly 4 options with only ONE correct answer.
3. The difficulty aligns with the requested level.
4. Explanations are highly detailed.
"""
