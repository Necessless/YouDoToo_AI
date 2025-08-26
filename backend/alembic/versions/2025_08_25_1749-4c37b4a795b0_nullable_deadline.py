"""Nullable deadline

Revision ID: 4c37b4a795b0
Revises: 1ef84ea64817
Create Date: 2025-08-25 17:49:57.168656

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '4c37b4a795b0'
down_revision: Union[str, None] = '1ef84ea64817'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('tasks', 'deadline',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True)



def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('tasks', 'deadline',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False)

