from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
from datetime import datetime, timezone, timedelta
import math

from ..core.database import get_db
from ..models.user import User
from ..models.flashcard import FlashcardDeck, Flashcard
from ..schemas.flashcard import FlashcardDeckCreate, FlashcardDeckOut, FlashcardCreate, FlashcardOut, FlashcardReviewSubmit
from .deps import get_current_user
from ..services.gamification import award_xp

router = APIRouter()

@router.post("/decks", response_model=FlashcardDeckOut)
async def create_deck(deck_in: FlashcardDeckCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    deck = FlashcardDeck(user_id=current_user.id, title=deck_in.title, description=deck_in.description)
    db.add(deck)
    await db.commit()
    await db.refresh(deck)
    return deck

@router.get("/decks", response_model=List[FlashcardDeckOut])
async def list_decks(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(FlashcardDeck).options(selectinload(FlashcardDeck.flashcards)).where(FlashcardDeck.user_id == current_user.id)
    )
    return result.scalars().all()

@router.post("/decks/{deck_id}/cards", response_model=FlashcardOut)
async def create_flashcard(deck_id: str, card_in: FlashcardCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Verify deck ownership
    result = await db.execute(select(FlashcardDeck).where(FlashcardDeck.id == deck_id, FlashcardDeck.user_id == current_user.id))
    deck = result.scalars().first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
        
    card = Flashcard(deck_id=deck_id, front=card_in.front, back=card_in.back)
    db.add(card)
    await db.commit()
    await db.refresh(card)
    return card

@router.get("/decks/{deck_id}/review", response_model=List[FlashcardOut])
async def get_cards_for_review(deck_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(FlashcardDeck).where(FlashcardDeck.id == deck_id, FlashcardDeck.user_id == current_user.id))
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Deck not found")
        
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(Flashcard).where(
            Flashcard.deck_id == deck_id,
            Flashcard.next_review_date <= now
        )
    )
    return result.scalars().all()

@router.post("/cards/{card_id}/review")
async def review_flashcard(card_id: str, review_in: FlashcardReviewSubmit, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(Flashcard).join(FlashcardDeck).where(Flashcard.id == card_id, FlashcardDeck.user_id == current_user.id)
    )
    card = result.scalars().first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
        
    # SM-2 Algorithm
    quality = review_in.quality
    if quality < 0 or quality > 5:
        raise HTTPException(status_code=400, detail="Quality must be between 0 and 5")
        
    if quality >= 3:
        if card.repetition == 0:
            card.interval = 1
        elif card.repetition == 1:
            card.interval = 6
        else:
            card.interval = math.ceil(card.interval * card.ease_factor)
        card.repetition += 1
    else:
        card.repetition = 0
        card.interval = 1
        
    card.ease_factor = card.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    if card.ease_factor < 1.3:
        card.ease_factor = 1.3
        
    card.next_review_date = datetime.now(timezone.utc) + timedelta(days=card.interval)
    await db.commit()
    
    # Award gamification XP
    gamification = await award_xp(db, current_user.id, 2)
    
    return {"message": "Review submitted", "next_review": card.next_review_date, "gamification": gamification}
