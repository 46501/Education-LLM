from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..core.database import get_db
from ..models.user import User
from ..models.document import Document
from ..services.document_parser import document_parser
from ..services.rag import rag_service
from .deps import get_current_user
from pydantic import BaseModel
from typing import List

router = APIRouter()

class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: str

    class Config:
        from_attributes = True

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Parse and chunk
    try:
        content = await file.read()
        chunks = document_parser.parse_and_chunk(content, file.content_type)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process document: {str(e)}")
    
    if not chunks:
        raise HTTPException(status_code=400, detail="No extractable text found in document")

    # Create document record
    document = Document(
        user_id=current_user.id,
        filename=file.filename,
        file_type=file.content_type
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)

    # Store embeddings in background or directly (awaiting directly for simplicity)
    try:
        await rag_service.store_chunks(db, document.id, chunks)
    except Exception as e:
        # Rollback
        await db.delete(document)
        await db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to generate embeddings: {str(e)}")

    return document

@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Document).where(Document.user_id == current_user.id))
    documents = result.scalars().all()
    return documents

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Document).where(Document.id == document_id, Document.user_id == current_user.id))
    document = result.scalars().first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    await db.delete(document)
    await db.commit()
    return {"message": "Document deleted successfully"}
