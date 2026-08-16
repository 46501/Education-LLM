from litellm import acompletion
import json
from ..core.config import settings
from ..prompts.quiz_generation import QUIZ_GENERATION_PROMPT, QuizGenerationResponse
from .rag import rag_service
from sqlalchemy.ext.asyncio import AsyncSession

class QuizGenerator:
    def __init__(self):
        self.model = "gpt-4o-mini" # Fast, cheap, supports structured output

    async def generate_questions(self, db: AsyncSession, user_id: str, subject: str, topic: str, difficulty: str, num_questions: int, question_type: str, use_rag: bool = False) -> QuizGenerationResponse:
        context = "No additional context provided."
        if use_rag:
            # Query the user's uploaded documents for this topic to form context
            # We use the topic name as the search query
            rag_results = await rag_service.retrieve_context(db, user_id, f"{subject} {topic}", top_k=10)
            if rag_results:
                context = "\n".join([f"Source [{r['filename']}]: {r['content']}" for r in rag_results])
            else:
                context = "No relevant context found in uploaded documents."

        prompt = QUIZ_GENERATION_PROMPT.format(
            num_questions=num_questions,
            topic=topic,
            subject=subject,
            difficulty=difficulty,
            question_type=question_type,
            context=context
        )

        if not settings.LLM_API_KEY or settings.LLM_API_KEY == "your_openai_api_key_here":
            return QuizGenerationResponse(
                questions=[
                    {
                        "question_text": f"What is a mock question for {topic}?",
                        "options": ["A", "B", "C", "D"],
                        "correct_answer": "A",
                        "explanation": "This is a mocked explanation.",
                        "difficulty": difficulty
                    },
                    {
                        "question_text": f"Another mock question for {topic}?",
                        "options": ["True", "False", "Neither", "Both"],
                        "correct_answer": "True",
                        "explanation": "This is a mocked explanation.",
                        "difficulty": difficulty
                    }
                ]
            )

        try:
            response = await acompletion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                api_key=settings.LLM_API_KEY or "dummy",
                response_format=QuizGenerationResponse,
                timeout=60
            )
            # litellm with response_format=PydanticClass returns the pydantic object in response.choices[0].message.content as a JSON string
            # wait, actually response_format=QuizGenerationResponse usually makes it return a json string that matches the schema, or if using Instructor it returns the object.
            # In pure litellm, if we pass response_format, we need to parse the JSON string.
            content_str = response.choices[0].message.content
            parsed = QuizGenerationResponse.model_validate_json(content_str)
            return parsed
        except Exception as e:
            raise Exception(f"Failed to generate questions: {e}")

quiz_generator = QuizGenerator()
