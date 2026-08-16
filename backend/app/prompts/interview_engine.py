from pydantic import BaseModel, Field
from typing import List

class InterviewEvaluation(BaseModel):
    score: float = Field(..., description="Score out of 10 for the previous answer.")
    technical_accuracy: float = Field(..., description="Score out of 10 for technical accuracy.")
    depth: float = Field(..., description="Score out of 10 for depth of knowledge.")
    clarity: float = Field(..., description="Score out of 10 for clarity of communication.")
    missing_points: List[str] = Field(..., description="Key points the student missed.")
    feedback: str = Field(..., description="Direct feedback to the student on their answer.")

class InterviewTurnResponse(BaseModel):
    evaluation: InterviewEvaluation = Field(..., description="Evaluation of the user's PREVIOUS answer.")
    next_question: str = Field(..., description="The next question to ask the user.")

INTERVIEW_TURN_PROMPT = """
You are an expert technical interviewer conducting an interview for a {role} role at the {level} level.
The primary topics for this interview are: {topics}.

You have just received the candidate's latest answer.
Evaluate their answer critically based on technical correctness, depth, and clarity.
Then, generate the NEXT question.
- If the answer was strong, ask a harder follow-up or move to the next topic.
- If the answer was weak or incomplete, ask a clarifying question or simpler follow-up.
- If the answer was wrong, politely correct them in the feedback and ask a related fundamental question.

Do NOT reveal the ideal answer to the new question.
Your response MUST match the JSON schema.
"""

class InterviewResultSchema(BaseModel):
    overall_score: float = Field(..., description="Overall score out of 10.")
    strengths: List[str] = Field(..., description="Key strengths identified during the interview.")
    weaknesses: List[str] = Field(..., description="Areas for improvement.")
    frequently_missed_concepts: List[str] = Field(..., description="Concepts the student struggled with.")
    communication_feedback: str = Field(..., description="Feedback on communication clarity and structure.")
    technical_recommendations: str = Field(..., description="Specific technical topics to study.")
    recommended_practice: str = Field(..., description="Actionable practice recommendations.")

INTERVIEW_COMPLETION_PROMPT = """
You are an expert technical interviewer. The interview has just concluded.
Review the entire conversation history and provide a comprehensive final evaluation.
Focus purely on technical merit and communication clarity. Do not invent psychological states.
Provide actionable, precise feedback.
"""
