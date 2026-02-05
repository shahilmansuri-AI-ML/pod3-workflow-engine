"""baseline pod3 schema

Revision ID: ce7dd3dfa2ba
Revises: 
Create Date: 2026-02-05 18:26:30.796032

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ce7dd3dfa2ba'
down_revision: Union[str, Sequence[str], None] = None
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
