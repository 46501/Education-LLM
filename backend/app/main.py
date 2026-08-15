from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import auth, chat, documents, quizzes, analytics, practice, personalization

app = FastAPI(
    title="Education LLM Platform",
    description="An intelligent tutoring and learning system.",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(quizzes.router, prefix="/api/quizzes", tags=["quizzes"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(practice.router, prefix="/api/practice", tags=["practice"])
app.include_router(personalization.router, prefix="/api/personalization", tags=["personalization"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}
