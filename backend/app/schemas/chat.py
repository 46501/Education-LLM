from pydantic import BaseModel
from typing import List, Optional

class MessageCreate(BaseModel):
    content: str
    conversation_id: Optional[str] = None

class MessageResponse(BaseModel):
    id: str
    role: str
    content: str

    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    id: str
    title: Optional[str]
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True
