"""subtask implementation

Revision ID: 1ef84ea64817
Revises: 6e560160f461
Create Date: 2025-08-25 17:42:32.254805

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '1ef84ea64817'
down_revision: Union[str, None] = '6e560160f461'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('tasks', sa.Column('is_completed', sa.Boolean(), nullable=False))
    op.add_column('tasks', sa.Column('parent_id', sa.UUID(), nullable=True))
    op.create_foreign_key(op.f('fk_tasks_parent_id_tasks'), 'tasks', 'tasks', ['parent_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f('fk_tasks_parent_id_tasks'), 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'parent_id')
    op.drop_column('tasks', 'is_completed')

