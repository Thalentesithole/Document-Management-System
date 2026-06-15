"""add_reviewer_approved_status

Revision ID: a3f1e5c82b91
Revises: 7ca4cd2460d0
Create Date: 2026-06-15 04:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3f1e5c82b91'
down_revision: Union[str, None] = '7ca4cd2460d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # PostgreSQL requires COMMIT before ALTER TYPE ... ADD VALUE
    op.execute("COMMIT")
    op.execute("ALTER TYPE documentstatusenum ADD VALUE IF NOT EXISTS 'reviewer_approved'")
    op.execute("BEGIN")


def downgrade() -> None:
    # PostgreSQL does not support removing values from an enum type.
    # This is a no-op; the value will remain in the enum.
    pass
