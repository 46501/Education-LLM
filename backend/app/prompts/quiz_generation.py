from pydantic import BaseModel, Field
from typing import List, Union, Optional

class QuizQuestionSchema(BaseModel):
    question_text: str = Field(..., description="The generated question text.")
    options: Optional[List[str]] = Field(None, description="A list of 4 options if the question type is MCQ. Null otherwise.")
    correct_answer: Union[str, List[str], float] = Field(..., description="The correct answer. String for MCQ/Short Answer, list for multiple correct, float for numerical.")
    explanation: str = Field(..., description="A detailed explanation of why the answer is correct.")
    difficulty: str = Field(..., description="The difficulty level of the question: BEGINNER, EASY, MEDIUM, HARD, EXPERT")

class QuizGenerationResponse(BaseModel):
    questions: List[QuizQuestionSchema] = Field(..., description="The generated list of questions.")

QUIZ_GENERATION_PROMPT = """
You are an expert AI tutor. Your task is to generate {num_questions} questions about the topic "{topic}" under the subject "{subject}".
The target difficulty is {difficulty}. 
The required question type is {question_type}.

If source material (context) is provided below, you MUST base your questions entirely on that material. Do NOT invent facts outside the provided context.

Context:
{context}

Ensure that:
1. The questions are educationally valuable and test understanding, not just trivia.
2. For MCQs, provide exactly 4 options. Only one option should be unambiguously correct.
3. The explanation clearly details why the correct answer is right and why distractors might be wrong.
"""
