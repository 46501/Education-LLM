import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.personalization import LearningMemory, RevisionSchedule
from app.services.spaced_repetition import update_revision_schedule
from app.core.database import Base
import uuid
import asyncio

# Setup in-memory sqlite for testing
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

@pytest_asyncio.fixture(scope="module")
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_spaced_repetition_initial(setup_db):
    async with TestingSessionLocal() as session:
        user_id = str(uuid.uuid4())
        topic_id = str(uuid.uuid4())
        
        # Accuracy is 90%
        schedule = await update_revision_schedule(session, user_id, topic_id, 90.0)
        
        assert schedule is not None
        assert schedule.interval_days == 1.0
        assert schedule.review_count == 1
        assert schedule.status == "UPCOMING"

@pytest.mark.asyncio
async def test_spaced_repetition_increase_interval(setup_db):
    async with TestingSessionLocal() as session:
        user_id = str(uuid.uuid4())
        topic_id = str(uuid.uuid4())
        
        # First practice
        schedule = await update_revision_schedule(session, user_id, topic_id, 90.0)
        # Second practice, accuracy 100%
        schedule = await update_revision_schedule(session, user_id, topic_id, 100.0)
        
        assert schedule.review_count == 2
        assert schedule.interval_days == 6.0
        assert schedule.ease_score > 2.5 # Ease score should increase

@pytest.mark.asyncio
async def test_spaced_repetition_poor_performance(setup_db):
    async with TestingSessionLocal() as session:
        user_id = str(uuid.uuid4())
        topic_id = str(uuid.uuid4())
        
        # First practice
        schedule = await update_revision_schedule(session, user_id, topic_id, 90.0)
        # Second practice
        schedule = await update_revision_schedule(session, user_id, topic_id, 90.0)
        # Third practice, poor performance
        schedule = await update_revision_schedule(session, user_id, topic_id, 20.0)
        
        assert schedule.review_count == 3
        assert schedule.interval_days == 1.0
        assert schedule.status == "DUE"
