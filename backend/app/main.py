from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.auth import router as auth_router
from .api.chat import router as chat_router
from .api.documents import router as documents_router
from .api.quizzes import router as quizzes_router
from .api.analytics import router as analytics_router
from .api.practice import router as practice_router
from .api.personalization import router as personalization_router
from .api.exams import router as exams_router
from .api.interviews import router as interviews_router

app = FastAPI(
    title="Education LLM Platform",
    description="An intelligent tutoring and learning system.",
    version="0.1.0"
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
app.include_router(documents_router, prefix="/api/documents", tags=["documents"])
app.include_router(quizzes_router, prefix="/api/quizzes", tags=["quizzes"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["analytics"])
app.include_router(practice_router, prefix="/api/practice", tags=["practice"])
app.include_router(personalization_router, prefix="/api/personalization", tags=["personalization"])
app.include_router(exams_router, prefix="/api/exams", tags=["exams"])
app.include_router(interviews_router, prefix="/api/interviews", tags=["interviews"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}
