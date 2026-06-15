"""add_returned_to_reviewer_status

Revision ID: b7d2e4f19c03
Revises: a3f1e5c82b91
Create Date: 2026-06-15 04:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7d2e4f19c03'
down_revision: Union[str, None] = 'a3f1e5c82b91'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # PostgreSQL requires COMMIT before ALTER TYPE ... ADD VALUE
    op.execute("COMMIT")
    op.execute("ALTER TYPE documentstatusenum ADD VALUE IF NOT EXISTS 'returned_to_reviewer'")
    op.execute("BEGIN")


def downgrade() -> None:
    # PostgreSQL does not support removing values from an enum type.
    pass
