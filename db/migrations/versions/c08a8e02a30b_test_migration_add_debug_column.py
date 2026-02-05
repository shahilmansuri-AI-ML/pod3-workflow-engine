"""test migration add debug column

Revision ID: c08a8e02a30b
Revises: ce7dd3dfa2ba
Create Date: 2026-02-05 18:32:05.752754

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c08a8e02a30b'
down_revision: Union[str, Sequence[str], None] = 'ce7dd3dfa2ba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    """Upgrade schema."""
    op.add_column(
        "executions",
        sa.Column("debug_note", sa.String(), nullable=True)
    )


def downgrade():
    """Downgrade schema."""
    op.drop_column("executions", "debug_note")
