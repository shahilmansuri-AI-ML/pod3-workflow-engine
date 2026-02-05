"""add integrity constraints

Revision ID: d4472e4d866f
Revises: 1cf025921509
Create Date: 2026-02-05 20:22:33.235468

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4472e4d866f'
down_revision: Union[str, Sequence[str], None] = '1cf025921509'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(
    "uq_execution_lock",
    "execution_locks",
    ["execution_id", "lock_type"]
    )

    op.create_unique_constraint(
    "uq_execution_step_key",
    "execution_steps",
    ["execution_id", "step_key"]
    )



def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("uq_execution_lock", "execution_locks", type_="unique")
    op.drop_constraint("uq_execution_step_key", "execution_steps", type_="unique")

