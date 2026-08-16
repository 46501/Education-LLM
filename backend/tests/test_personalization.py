"""
Comprehensive Phase 4 Personalization Engine tests.

Tests cover:
1. Spaced repetition adaptive intervals
2. Learning memory analysis (weakness, strength, misconception, achievement)
3. Scoring engine with gradual difficulty scaling
4. Streak tracking (meaningful activities only)
5. User data isolation
"""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import sqlalchemy

# ---- SQLite compatibility: compile PostgreSQL-specific types as TEXT ----
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
from sqlalchemy.ext.compiler import compiles


@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(element, compiler, **kw):
    return "TEXT"


@compiles(Vector, "sqlite")
def compile_vector_sqlite(element, compiler, **kw):
    return "TEXT"


# ---- Now import models ----
from app.core.database import Base
from app.models.personalization import (
    LearningProfile, LearningPreference, LearningMemory,
    RevisionSchedule, StudyPlan, StudyPlanItem, StudySession
)
from app.models.learning import (
    Subject, Topic, TopicMastery, Mistake, Question
)
from app.models.user import User
from app.services.spaced_repetition import update_revision_schedule, get_due_revisions, INTERVAL_LADDER
from app.services.scoring import ScoringEngine, DIFFICULTY_LEVELS
from app.services.learning_memory import evaluate_and_store_memory, get_memories
from app.services.streak import update_streak
import uuid
from datetime import datetime, timedelta, timezone

# Setup in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(scope="module")
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def _create_user(session) -> User:
    """Helper: create a user record in the database."""
    user = User(
        id=str(uuid.uuid4()),
        email=f"test_{uuid.uuid4().hex[:8]}@test.com",
        password_hash="fakehash"
    )
    session.add(user)
    await session.flush()
    return user


async def _create_topic(session, name=None) -> Topic:
    """Helper: create a subject and topic."""
    topic_name = name or f"Topic_{uuid.uuid4().hex[:6]}"
    subj = Subject(name=f"Subject_{uuid.uuid4().hex[:6]}")
    session.add(subj)
    await session.flush()
    topic = Topic(name=topic_name, subject_id=subj.id)
    session.add(topic)
    await session.flush()
    return topic


# ============================================================
# 1. SPACED REPETITION TESTS
# ============================================================

@pytest.mark.asyncio
async def test_spaced_repetition_initial_creates_schedule(setup_db):
    """First encounter with a topic should create a schedule at 1-day interval."""
    async with TestingSessionLocal() as session:
        user = await _create_user(session)
        topic = await _create_topic(session)

        schedule = await update_revision_schedule(session, user.id, topic.id, 90.0)

        assert schedule is not None
        assert schedule.interval_days == 1.0
        assert schedule.review_count == 1
        assert schedule.status == "UPCOMING"


@pytest.mark.asyncio
async def test_spaced_repetition_good_performance_advances(setup_db):
    """Good performance (>=60%) should advance interval on the ladder."""
    async with TestingSessionLocal() as session:
        user = await _create_user(session)
        topic = await _create_topic(session)

        # First review → 1 day
        schedule = await update_revision_schedule(session, user.id, topic.id, 70.0)
        assert schedule.interval_days == 1.0

        # Second review (good, 60-85%) → advances 1 rung to 3 days
        schedule = await update_revision_schedule(session, user.id, topic.id, 75.0)
        assert schedule.interval_days == 3.0
        assert schedule.review_count == 2


@pytest.mark.asyncio
async def test_spaced_repetition_great_performance_advances_two(setup_db):
    """Great performance (>=85%) should advance 2 rungs."""
    async with TestingSessionLocal() as session:
        user = await _create_user(session)
        topic = await _create_topic(session)

        # First review → 1 day (rung 0)
        schedule = await update_revision_schedule(session, user.id, topic.id, 95.0)
        assert schedule.interval_days == 1.0

        # Second review (great >=85%) → advances 2 rungs: 1→7
        schedule = await update_revision_schedule(session, user.id, topic.id, 95.0)
        assert schedule.interval_days == 7.0


@pytest.mark.asyncio
async def test_spaced_repetition_poor_performance_resets(setup_db):
    """Poor performance (<40%) should reset interval to 1 day and status to DUE."""
    async with TestingSessionLocal() as session:
        user = await _create_user(session)
        topic = await _create_topic(session)

        # Build up interval
        await update_revision_schedule(session, user.id, topic.id, 90.0)  # 1 day
        await update_revision_schedule(session, user.id, topic.id, 90.0)  # 7 days

        # Poor performance resets
        schedule = await update_revision_schedule(session, user.id, topic.id, 20.0)
        assert schedule.interval_days == 1.0
        assert schedule.status == "DUE"
        assert schedule.review_count == 3


@pytest.mark.asyncio
async def test_spaced_repetition_mediocre_drops_one(setup_db):
    """Mediocre performance (40-60%) should drop interval by one rung."""
    async with TestingSessionLocal() as session:
        user = await _create_user(session)
        topic = await _create_topic(session)

        # Build up to 7-day interval (rung 2)
        await update_revision_schedule(session, user.id, topic.id, 90.0)  # → 1 day
        await update_revision_schedule(session, user.id, topic.id, 90.0)  # → 7 days

        # Mediocre performance → drop to rung 1 (3 days)
        schedule = await update_revision_schedule(session, user.id, topic.id, 50.0)
        assert schedule.interval_days == 3.0
        assert schedule.status == "UPCOMING"


@pytest.mark.asyncio
async def test_spaced_repetition_interval_never_exceeds_365(setup_db):
    """Interval should cap at 365 days."""
    async with TestingSessionLocal() as session:
        user = await _create_user(session)
        topic = await _create_topic(session)

        # Repeatedly advance
        for _ in range(20):
            await update_revision_schedule(session, user.id, topic.id, 95.0)

        schedule = await update_revision_schedule(session, user.id, topic.id, 95.0)
        assert schedule.interval_days <= 365.0


# ============================================================
# 2. SCORING & DIFFICULTY SCALING TESTS
# ============================================================

@pytest.mark.asyncio
async def test_scoring_initial_mastery(setup_db):
    """First correct answer should create mastery record."""
    async with TestingSessionLocal() as session:
        user = await _create_user(session)
        topic = await _create_topic(session, "Scoring Test")

        scoring = ScoringEngine()
        mastery = await scoring.update_mastery(session, user.id, topic.id, True, "BEGINNER")

        assert mastery.questions_attempted == 1
        assert mastery.questions_correct == 1
        assert mastery.accuracy == 100.0


@pytest.mark.asyncio
async def test_scoring_no_extreme_difficulty_jump(setup_db):
    """Difficulty should never jump more than 1 level at a time."""
    async with TestingSessionLocal() as session:
        user = await _create_user(session)
        topic = await _create_topic(session, "Difficulty Jump Test")

        scoring = ScoringEngine()

        # Start at BEGINNER
        mastery = await scoring.update_mastery(session, user.id, topic.id, True, "BEGINNER")
        initial_diff = mastery.current_difficulty
        initial_idx = DIFFICULTY_LEVELS.index(initial_diff)

        # Even with perfect score, should advance at most 1 level
        mastery = await scoring.update_mastery(session, user.id, topic.id, True, "BEGINNER")
        new_idx = DIFFICULTY_LEVELS.index(mastery.current_difficulty)
        assert abs(new_idx - initial_idx) <= 1


@pytest.mark.asyncio
async def test_scoring_difficulty_never_jumps_multiple(setup_db):
    """Even after many correct answers, each step should be at most ±1 level."""
    async with TestingSessionLocal() as session:
        user = await _create_user(session)
        topic = await _create_topic(session, "Multi Step Difficulty")

        scoring = ScoringEngine()

        prev_difficulty = "BEGINNER"
        mastery = None
        for i in range(15):
            difficulty = mastery.current_difficulty if mastery else "BEGINNER"
            mastery = await scoring.update_mastery(
                session, user.id, topic.id, True, difficulty
            )
            curr_idx = DIFFICULTY_LEVELS.index(mastery.current_difficulty)
            prev_idx = DIFFICULTY_LEVELS.index(prev_difficulty)
            assert abs(curr_idx - prev_idx) <= 1, (
                f"Jump from {prev_difficulty} to {mastery.current_difficulty} at step {i}"
            )
            prev_difficulty = mastery.current_difficulty


@pytest.mark.asyncio
async def test_scoring_mastery_decreases_on_wrong(setup_db):
    """Wrong answers should decrease mastery score."""
    async with TestingSessionLocal() as session:
        user = await _create_user(session)
        topic = await _create_topic(session, "Wrong Answer Test")

        scoring = ScoringEngine()

        # Build some mastery
        for _ in range(5):
            mastery = await scoring.update_mastery(session, user.id, topic.id, True, "MEDIUM")

        high_score = mastery.mastery_score

        # Get it wrong
        mastery = await scoring.update_mastery(session, user.id, topic.id, False, "MEDIUM")
        assert mastery.mastery_score < high_score


# ============================================================
# 3. LEARNING MEMORY TESTS
# ============================================================

@pytest.mark.asyncio
async def test_learning_memory_weakness_detection(setup_db):
    """Low accuracy + multiple mistakes should create WEAKNESS memory."""
    async with TestingSessionLocal() as session:
        user = await _create_user(session)
        topic = await _create_topic(session, "Weakness Test Topic")

        # Create mastery with low accuracy
        mastery = TopicMastery(
            user_id=user.id, topic_id=topic.id,
            mastery_score=20.0, questions_attempted=10,
            questions_correct=3, questions_incorrect=7, accuracy=30.0
        )
        session.add(mastery)

        # Create a question (needed as FK for mistakes)
        question = Question(
            subject_id=topic.subject_id, topic_id=topic.id,
            question_text="Test Q", question_type="MCQ",
            difficulty="EASY", correct_answer="A"
        )
        session.add(question)
        await session.flush()

        for _ in range(3):
            m = Mistake(
                user_id=user.id, topic_id=topic.id, question_id=question.id,
                error_category="CONCEPTUAL_ERROR", student_answer="B"
            )
            session.add(m)
        await session.commit()

        await evaluate_and_store_memory(session, user.id, topic.id)

        memories = await get_memories(session, user.id, topic_id=topic.id, memory_type="WEAKNESS")
        assert len(memories) == 1
        assert "struggles" in memories[0].content.lower()


@pytest.mark.asyncio
async def test_learning_memory_strength_detection(setup_db):
    """High accuracy + enough attempts should create STRENGTH memory."""
    async with TestingSessionLocal() as session:
        user = await _create_user(session)
        topic = await _create_topic(session, "Strength Test Topic")

        mastery = TopicMastery(
            user_id=user.id, topic_id=topic.id,
            mastery_score=85.0, questions_attempted=10,
            questions_correct=9, questions_incorrect=1, accuracy=90.0
        )
        session.add(mastery)
        await session.commit()

        await evaluate_and_store_memory(session, user.id, topic.id)

        memories = await get_memories(session, user.id, topic_id=topic.id, memory_type="STRENGTH")
        assert len(memories) == 1
        assert "excels" in memories[0].content.lower()


@pytest.mark.asyncio
async def test_learning_memory_misconception_detection(setup_db):
    """Repeated same-type errors should create MISCONCEPTION memory."""
    async with TestingSessionLocal() as session:
        user = await _create_user(session)
        topic = await _create_topic(session, "Misconception Test Topic")

        mastery = TopicMastery(
            user_id=user.id, topic_id=topic.id,
            mastery_score=40.0, questions_attempted=8,
            questions_correct=4, questions_incorrect=4, accuracy=50.0
        )
        session.add(mastery)

        question = Question(
            subject_id=topic.subject_id, topic_id=topic.id,
            question_text="Test", question_type="MCQ",
            difficulty="MEDIUM", correct_answer="A"
        )
        session.add(question)
        await session.flush()

        # Create 4 mistakes with the SAME category
        for _ in range(4):
            m = Mistake(
                user_id=user.id, topic_id=topic.id, question_id=question.id,
                error_category="CALCULATION_ERROR", student_answer="wrong"
            )
            session.add(m)
        await session.commit()

        await evaluate_and_store_memory(session, user.id, topic.id)

        memories = await get_memories(session, user.id, topic_id=topic.id, memory_type="MISCONCEPTION")
        assert len(memories) >= 1
        assert "calculation error" in memories[0].content.lower()


# ============================================================
# 4. STREAK TRACKING TESTS
# ============================================================

@pytest.mark.asyncio
async def test_streak_first_activity(setup_db):
    """First-ever activity should start streak at 1."""
    async with TestingSessionLocal() as session:
        user = await _create_user(session)

        profile = await update_streak(session, user.id)

        assert profile.current_streak == 1
        assert profile.longest_streak == 1


@pytest.mark.asyncio
async def test_streak_same_day_no_increase(setup_db):
    """Multiple activities on the same day should NOT increase streak."""
    async with TestingSessionLocal() as session:
        user = await _create_user(session)

        profile = await update_streak(session, user.id)
        assert profile.current_streak == 1

        # Another activity same day
        profile = await update_streak(session, user.id)
        assert profile.current_streak == 1


@pytest.mark.asyncio
async def test_streak_consecutive_days_increases(setup_db):
    """Activities on consecutive days should increase streak."""
    async with TestingSessionLocal() as session:
        user = await _create_user(session)

        # Day 1
        profile = await update_streak(session, user.id)
        assert profile.current_streak == 1

        # Simulate yesterday by manually setting last_active_date
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        profile.last_active_date = yesterday
        await session.commit()

        # Day 2 (today)
        profile = await update_streak(session, user.id)
        assert profile.current_streak == 2
        assert profile.longest_streak == 2


@pytest.mark.asyncio
async def test_streak_gap_resets(setup_db):
    """Missing a full day should reset streak to 1."""
    async with TestingSessionLocal() as session:
        user = await _create_user(session)

        profile = await update_streak(session, user.id)
        profile.current_streak = 5
        profile.longest_streak = 5
        profile.last_active_date = datetime.now(timezone.utc) - timedelta(days=3)
        await session.commit()

        profile = await update_streak(session, user.id)
        assert profile.current_streak == 1
        assert profile.longest_streak == 5  # Longest should be preserved


# ============================================================
# 5. USER DATA ISOLATION TESTS
# ============================================================

@pytest.mark.asyncio
async def test_user_isolation_revision_schedules(setup_db):
    """User A's revision schedules should not be visible to User B."""
    async with TestingSessionLocal() as session:
        user_a = await _create_user(session)
        user_b = await _create_user(session)
        topic = await _create_topic(session)

        await update_revision_schedule(session, user_a.id, topic.id, 80.0)

        # User B should have no revisions
        from sqlalchemy.future import select
        result = await session.execute(
            select(RevisionSchedule).where(RevisionSchedule.user_id == user_b.id)
        )
        assert result.scalars().all() == []


@pytest.mark.asyncio
async def test_user_isolation_learning_memories(setup_db):
    """User A's memories should not be visible to User B."""
    async with TestingSessionLocal() as session:
        user_a = await _create_user(session)
        user_b = await _create_user(session)

        mem = LearningMemory(
            user_id=user_a.id, memory_type="STRENGTH",
            content="Test memory", confidence=0.9, source="TEST"
        )
        session.add(mem)
        await session.commit()

        # User B should see nothing
        memories = await get_memories(session, user_b.id)
        assert len(memories) == 0


@pytest.mark.asyncio
async def test_user_isolation_streaks(setup_db):
    """User A's streak should not affect User B."""
    async with TestingSessionLocal() as session:
        user_a = await _create_user(session)
        user_b = await _create_user(session)

        # User A builds streak
        profile_a = await update_streak(session, user_a.id)
        assert profile_a.current_streak == 1

        # User B's profile should be independent
        profile_b = await update_streak(session, user_b.id)
        assert profile_b.current_streak == 1

        # Verify they are different records
        assert profile_a.id != profile_b.id
