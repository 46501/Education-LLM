from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import auth, chat

app = FastAPI(
    title="Education LLM Platform",
    description="API for the Education LLM Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}
