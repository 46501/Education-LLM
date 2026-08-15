from pydantic import BaseModel, Field

class MistakeClassificationResponse(BaseModel):
    category: str = Field(..., description="Must be one of: CONCEPTUAL_ERROR, CALCULATION_ERROR, CARELESS_ERROR, MISUNDERSTANDING, INCOMPLETE_ANSWER, SYNTAX_ERROR, LOGICAL_ERROR, UNKNOWN")
    explanation: str = Field(..., description="A short explanation of what exactly went wrong in the student's thought process.")

MISTAKE_CLASSIFICATION_PROMPT = """
You are an AI diagnostic system. Analyze why the student got this question wrong.
Topic: {topic}
Question: {question}
Expected Correct Answer: {correct_answer}
Student's Incorrect Answer: {student_answer}

Identify the root cause of the error. Categorize it strictly into one of the allowed categories.
"""
