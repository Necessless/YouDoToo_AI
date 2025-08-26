"""Add model subtask for better relations

Revision ID: d650d6262436
Revises: 4c37b4a795b0
Create Date: 2025-08-26 12:59:15.684980

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd650d6262436'
down_revision: Union[str, None] = '4c37b4a795b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('subtasks',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('is_completed', sa.Boolean(), nullable=False),
    sa.Column('parent_id', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['parent_id'], ['tasks.id'], name=op.f('fk_subtasks_parent_id_tasks'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_subtasks'))
    )
    op.drop_constraint(op.f('fk_tasks_parent_id_tasks'), 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'parent_id')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('tasks', sa.Column('parent_id', sa.UUID(), autoincrement=False, nullable=True))
    op.create_foreign_key(op.f('fk_tasks_parent_id_tasks'), 'tasks', 'tasks', ['parent_id'], ['id'], ondelete='CASCADE')
    op.drop_table('subtasks')
