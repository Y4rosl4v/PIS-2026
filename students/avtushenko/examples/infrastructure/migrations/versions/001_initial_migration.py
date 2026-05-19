"""initial_migration

Revision ID: 001
Revises: 
Create Date: 2026-05-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create courses table
    op.create_table(
        'courses',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.String(1000), nullable=False),
        sa.Column('rating', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
    )
    
    # Create lessons table
    op.create_table(
        'lessons',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('course_id', sa.String(50), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('video_url', sa.String(500), nullable=False),
        sa.Column('test_question_text', sa.String(500), nullable=True),
        sa.Column('test_options', postgresql.JSON(), nullable=True),
        sa.Column('test_correct_index', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
    )
    
    # Create enrollments table
    op.create_table(
        'enrollments',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('student_id', sa.String(50), nullable=False),
        sa.Column('course_id', sa.String(50), nullable=False),
        sa.Column('completed_lessons', postgresql.JSON(), default=list),
        sa.Column('test_results', postgresql.JSON(), default=dict),
        sa.Column('total_lessons', sa.Integer(), default=0),
        sa.Column('started_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
    )
    
    # Create indexes
    op.create_index('idx_enrollments_student_id', 'enrollments', ['student_id'])
    op.create_index('idx_enrollments_course_id', 'enrollments', ['course_id'])
    op.create_index('idx_lessons_course_id', 'lessons', ['course_id'])

def downgrade() -> None:
    op.drop_table('enrollments')
    op.drop_table('lessons')
    op.drop_table('courses')