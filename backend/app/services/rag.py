from litellm import aembedding
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text
from ..models.document import DocumentChunk
from ..core.config import settings

class RAGService:
    def __init__(self):
        self.embedding_model = "text-embedding-3-small"

    async def generate_embedding(self, content: str) -> list[float]:
        response = await aembedding(
            model=self.embedding_model,
            input=content,
            api_key=settings.LLM_API_KEY or "dummy_key"
        )
        return response.data[0]['embedding']

    async def store_chunks(self, db: AsyncSession, document_id: str, chunks: list[dict]):
        for chunk in chunks:
            embedding = await self.generate_embedding(chunk["content"])
            doc_chunk = DocumentChunk(
                document_id=document_id,
                content=chunk["content"],
                page_number=chunk["page_number"],
                embedding=embedding
            )
            db.add(doc_chunk)
        await db.commit()

    async def retrieve_context(self, db: AsyncSession, user_id: str, query: str, top_k: int = 4) -> list[dict]:
        query_embedding = await self.generate_embedding(query)
        
        # We must join with documents to filter by user_id
        # similarity threshold can be adjusted
        stmt = text("""
            SELECT c.content, c.page_number, d.filename, 
                   1 - (c.embedding <=> :embedding) AS similarity
            FROM document_chunks c
            JOIN documents d ON c.document_id = d.id
            WHERE d.user_id = :user_id
            ORDER BY c.embedding <=> :embedding
            LIMIT :top_k
        """)
        
        result = await db.execute(stmt, {
            "embedding": str(query_embedding), # string cast for pgvector
            "user_id": user_id,
            "top_k": top_k
        })
        
        rows = result.fetchall()
        context = []
        for row in rows:
            if row.similarity > 0.3: # Threshold
                context.append({
                    "content": row.content,
                    "page_number": row.page_number,
                    "filename": row.filename,
                    "similarity": row.similarity
                })
        
        return context

rag_service = RAGService()
