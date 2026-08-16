from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi.responses import StreamingResponse
import json
from litellm import acompletion
from ..models.personalization import LearningPreference, LearningMemory

from ..core.database import get_db
from ..core.config import settings
from ..models.user import User
from ..models.chat import Conversation, Message
from ..schemas.chat import MessageCreate, MessageResponse, ConversationResponse
from .deps import get_current_user

router = APIRouter()

SYSTEM_PROMPT = """You are an expert AI Tutor. Your goal is to guide the student towards the answer rather than just giving it away.
Use the Socratic method when appropriate.
Keep your responses educational and encouraging.
"""

@router.get("/", response_model=list[ConversationResponse])
async def get_conversations(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Conversation).where(Conversation.user_id == current_user.id))
    conversations = result.scalars().all()
    return conversations

@router.post("/")
async def chat(request: MessageCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if request.conversation_id:
        result = await db.execute(select(Conversation).where(Conversation.id == request.conversation_id, Conversation.user_id == current_user.id))
        conversation = result.scalars().first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = Conversation(user_id=current_user.id, title=request.content[:50])
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

    # Save user message
    user_message = Message(conversation_id=conversation.id, role="user", content=request.content)
    db.add(user_message)
    await db.commit()

    # Get history
    result = await db.execute(select(Message).where(Message.conversation_id == conversation.id).order_by(Message.created_at))
    history = result.scalars().all()

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Retrieve context from RAG
    try:
        from ..services.rag import rag_service
        context = await rag_service.retrieve_context(db, current_user.id, request.content)
        if context:
            context_str = "Use the following context to answer the student's question. Always cite the source filename and page number.\n\n"
            for c in context:
                context_str += f"Source: [{c['filename']}, Page {c['page_number']}]\nText: \"\"\"{c['content']}\"\"\"\n\n"
            
            # Inject context into system prompt
            messages[0]["content"] += "\n" + context_str
    except Exception as e:
        print(f"RAG retrieval failed: {e}")

    # Inject Personalization Context
    try:
        pref_res = await db.execute(select(LearningPreference).where(LearningPreference.user_id == current_user.id))
        pref = pref_res.scalar_one_or_none()
        
        mem_res = await db.execute(select(LearningMemory).where(LearningMemory.user_id == current_user.id).order_by(LearningMemory.created_at.desc()).limit(3))
        mems = mem_res.scalars().all()
        
        pers_context = "\n\n--- STUDENT PROFILE ---\n"
        if pref:
            pers_context += f"Explanation Style: {pref.explanation_style}\n"
            pers_context += f"Difficulty Preference: {pref.difficulty_preference}\n"
        
        if mems:
            pers_context += "Learning Memories (Things to remember about this student):\n"
            for m in mems:
                pers_context += f"- [{m.memory_type}] {m.content}\n"
                
        messages[0]["content"] += pers_context
    except Exception as e:
        print(f"Personalization retrieval failed: {e}")

    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})

    async def generate():
        if not settings.LLM_API_KEY or settings.LLM_API_KEY == "your_openai_api_key_here":
            dummy_resp = "This is a mocked AI Tutor response. Context injected successfully."
            yield f"data: {json.dumps({'content': dummy_resp})}\n\n"
            
            ai_message = Message(conversation_id=conversation.id, role="tutor", content=dummy_resp)
            db.add(ai_message)
            await db.commit()
            return

        response = await acompletion(
            model="gemini/gemini-1.5-pro", # Defaulting to gemini or openai based on settings
            messages=messages,
            api_key=settings.LLM_API_KEY or "dummy_key", # Assuming litellm will handle or we mock
            stream=True
        )
        full_reply = ""
        async for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_reply += content
                yield f"data: {json.dumps({'content': content})}\n\n"
        
        # Save AI reply
        ai_message = Message(conversation_id=conversation.id, role="tutor", content=full_reply)
        db.add(ai_message)
        await db.commit()

    return StreamingResponse(generate(), media_type="text/event-stream")
