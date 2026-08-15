"""phase_2_and_3

Revision ID: 28d8464dea39
Revises: ceb7a9c5bda7
Create Date: 2026-08-15 18:21:37.078445

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '28d8464dea39'
down_revision: Union[str, Sequence[str], None] = 'ceb7a9c5bda7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # Phase 2: Documents and Chunks
    op.create_table('documents',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('subject_id', sa.String(), nullable=True),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('file_type', sa.String(), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('document_chunks',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('document_id', sa.String(), nullable=False),
        sa.Column('content', sa.String(), nullable=False),
        sa.Column('embedding', pgvector.sqlalchemy.vector.VECTOR(dim=1536), nullable=True),
        sa.Column('page_number', sa.Integer(), nullable=True),
        sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Phase 3: Learning Engine
    op.create_table('subjects',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    op.create_table('topics',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('subject_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('parent_topic_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['parent_topic_id'], ['topics.id'], ),
        sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('questions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('subject_id', sa.String(), nullable=False),
        sa.Column('topic_id', sa.String(), nullable=False),
        sa.Column('question_text', sa.String(), nullable=False),
        sa.Column('question_type', sa.String(), nullable=False),
        sa.Column('difficulty', sa.String(), nullable=False),
        sa.Column('options', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('correct_answer', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('explanation', sa.String(), nullable=True),
        sa.Column('source_document_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['source_document_id'], ['documents.id'], ),
        sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('quizzes',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('subject_id', sa.String(), nullable=True),
        sa.Column('topic_id', sa.String(), nullable=True),
        sa.Column('difficulty', sa.String(), nullable=True),
        sa.Column('number_of_questions', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('quiz_questions',
        sa.Column('quiz_id', sa.String(), nullable=False),
        sa.Column('question_id', sa.String(), nullable=False),
        sa.Column('question_order', sa.Integer(), nullable=False),
        sa.Column('marks', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ),
        sa.ForeignKeyConstraint(['quiz_id'], ['quizzes.id'], ),
        sa.PrimaryKeyConstraint('quiz_id', 'question_id')
    )

    op.create_table('question_attempts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('quiz_id', sa.String(), nullable=True),
        sa.Column('question_id', sa.String(), nullable=False),
        sa.Column('submitted_answer', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('max_score', sa.Float(), nullable=False),
        sa.Column('evaluation_feedback', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('time_taken', sa.Integer(), nullable=True),
        sa.Column('attempted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ),
        sa.ForeignKeyConstraint(['quiz_id'], ['quizzes.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('topic_mastery',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('topic_id', sa.String(), nullable=False),
        sa.Column('mastery_score', sa.Float(), nullable=True),
        sa.Column('questions_attempted', sa.Integer(), nullable=True),
        sa.Column('questions_correct', sa.Integer(), nullable=True),
        sa.Column('questions_incorrect', sa.Integer(), nullable=True),
        sa.Column('accuracy', sa.Float(), nullable=True),
        sa.Column('current_difficulty', sa.String(), nullable=True),
        sa.Column('last_practiced', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('mistakes',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('topic_id', sa.String(), nullable=False),
        sa.Column('question_id', sa.String(), nullable=False),
        sa.Column('error_category', sa.String(), nullable=False),
        sa.Column('student_answer', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('explanation', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('mistakes')
    op.drop_table('topic_mastery')
    op.drop_table('question_attempts')
    op.drop_table('quiz_questions')
    op.drop_table('quizzes')
    op.drop_table('questions')
    op.drop_table('topics')
    op.drop_table('subjects')
    op.drop_table('document_chunks')
    op.drop_table('documents')
    op.execute('DROP EXTENSION IF EXISTS vector')
