from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class FlashcardBase(BaseModel):
    front: str
    back: str

class FlashcardCreate(FlashcardBase):
    pass

class FlashcardOut(FlashcardBase):
    id: str
    deck_id: str
    next_review_date: datetime
    
    class Config:
        from_attributes = True

class FlashcardDeckBase(BaseModel):
    title: str
    description: Optional[str] = None

class FlashcardDeckCreate(FlashcardDeckBase):
    pass

class FlashcardDeckOut(FlashcardDeckBase):
    id: str
    user_id: str
    created_at: datetime
    flashcards: List[FlashcardOut] = []

    class Config:
        from_attributes = True

class FlashcardReviewSubmit(BaseModel):
    quality: int # 0-5 scale of how easy it was to remember
