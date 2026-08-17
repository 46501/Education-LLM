from .llm import safe_acompletion
import json
from ..core.config import settings
from ..prompts.answer_evaluation import ANSWER_EVALUATION_PROMPT, AnswerEvaluationResponse
from ..prompts.mistake_classification import MISTAKE_CLASSIFICATION_PROMPT, MistakeClassificationResponse

class AnswerEvaluator:
    def __init__(self):
        self.model = "gpt-4o-mini"

    def evaluate_mcq(self, student_answer: str, correct_answer: str) -> dict:
        is_correct = student_answer.strip().lower() == correct_answer.strip().lower()
        return {
            "score": 1.0 if is_correct else 0.0,
            "is_correct": is_correct,
            "feedback": "Correct!" if is_correct else "Incorrect.",
            "mistakes": [] if is_correct else ["Selected the wrong option."]
        }

    def evaluate_numerical(self, student_answer: float, correct_answer: float, tolerance: float = 0.01) -> dict:
        try:
            student_val = float(student_answer)
            correct_val = float(correct_answer)
            is_correct = abs(student_val - correct_val) <= tolerance
            return {
                "score": 1.0 if is_correct else 0.0,
                "is_correct": is_correct,
                "feedback": "Correct!" if is_correct else "Incorrect.",
                "mistakes": [] if is_correct else ["Calculation error or out of tolerance."]
            }
        except:
            return {
                "score": 0.0,
                "is_correct": False,
                "feedback": "Invalid numeric format.",
                "mistakes": ["Failed to parse numeric answer."]
            }

    async def evaluate_short_answer(self, topic: str, question: str, correct_answer: str, student_answer: str) -> dict:
        prompt = ANSWER_EVALUATION_PROMPT.format(
            topic=topic,
            question=question,
            correct_answer=correct_answer,
            student_answer=student_answer
        )
        
        try:
            response = await safe_acompletion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                api_key=settings.LLM_API_KEY or "dummy",
                response_format=AnswerEvaluationResponse
            )
            parsed = AnswerEvaluationResponse.model_validate_json(response.choices[0].message.content)
            return parsed.model_dump()
        except Exception as e:
            raise Exception(f"Failed to evaluate short answer: {e}")

    async def classify_mistake(self, topic: str, question: str, correct_answer: str, student_answer: str) -> dict:
        prompt = MISTAKE_CLASSIFICATION_PROMPT.format(
            topic=topic,
            question=question,
            correct_answer=correct_answer,
            student_answer=student_answer
        )
        try:
            response = await safe_acompletion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                api_key=settings.LLM_API_KEY or "dummy",
                response_format=MistakeClassificationResponse
            )
            parsed = MistakeClassificationResponse.model_validate_json(response.choices[0].message.content)
            return parsed.model_dump()
        except:
            # Fallback
            return {"category": "UNKNOWN", "explanation": "Failed to classify mistake."}

answer_evaluator = AnswerEvaluator()
