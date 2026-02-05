"""remove debug column

Revision ID: 1cf025921509
Revises: c08a8e02a30b
Create Date: 2026-02-05 18:52:46.768390

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1cf025921509'
down_revision: Union[str, Sequence[str], None] = 'c08a8e02a30b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column("executions", "debug_note")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "executions",
        sa.Column("debug_note", sa.String(), nullable=True)
    )
