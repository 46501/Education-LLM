from sqlalchemy import Column, String, DateTime, func, Integer
from ..core.database import Base
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="student")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
