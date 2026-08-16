from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float, Text, Boolean, func
from sqlalchemy.orm import relationship
from ..core.database import Base
import uuid

class FlashcardDeck(Base):
    __tablename__ = "flashcard_decks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    flashcards = relationship("Flashcard", back_populates="deck", cascade="all, delete-orphan")

class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    deck_id = Column(String, ForeignKey("flashcard_decks.id"), nullable=False)
    front = Column(Text, nullable=False)
    back = Column(Text, nullable=False)
    
    # SM-2 Algorithm Fields for Spaced Repetition
    interval = Column(Integer, default=0, nullable=False) # days until next review
    repetition = Column(Integer, default=0, nullable=False) # consecutive correct answers
    ease_factor = Column(Float, default=2.5, nullable=False) # how easy the card is
    next_review_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    deck = relationship("FlashcardDeck", back_populates="flashcards")
