from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
import logging
import uuid

from .core.exceptions import AppError
from .api.auth import router as auth_router
from .api.chat import router as chat_router
from .api.documents import router as documents_router
from .api.quizzes import router as quizzes_router
from .api.analytics import router as analytics_router
from .api.practice import router as practice_router
from .api.personalization import router as personalization_router
from .api.exams import router as exams_router
from .api.interviews import router as interviews_router
from .api.flashcards import router as flashcards_router

app = FastAPI(
    title="Education LLM Platform",
    description="An intelligent tutoring and learning system.",
    version="0.1.0"
)

logger = logging.getLogger("uvicorn.error")

def get_cors_headers(request: Request) -> dict:
    origin = request.headers.get("origin")
    if origin:
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
        }
    return {}

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}},
        headers=get_cors_headers(request)
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    code = "HTTP_ERROR"
    if exc.status_code == 400: code = "BAD_REQUEST"
    if exc.status_code == 401: code = "UNAUTHORIZED"
    if exc.status_code == 403: code = "FORBIDDEN"
    if exc.status_code == 404: code = "RESOURCE_NOT_FOUND"
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": code, "message": str(exc.detail)}},
        headers=get_cors_headers(request)
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": {"code": "VALIDATION_ERROR", "message": "Invalid request format or missing required fields."}},
        headers=get_cors_headers(request)
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    req_id = str(uuid.uuid4())
    logger.error(f"DATABASE_ERROR request_id={req_id} path={request.url.path} error={str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "DATABASE_ERROR", "message": "Unable to process your request right now. Please try again."}},
        headers=get_cors_headers(request)
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    req_id = str(uuid.uuid4())
    logger.error(f"UNEXPECTED_ERROR request_id={req_id} path={request.url.path} error={str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred. Please try again later."}},
        headers=get_cors_headers(request)
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
app.include_router(flashcards_router, prefix="/api/flashcards", tags=["flashcards"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}

