"""3stage_workflow

Revision ID: 7ca4cd2460d0
Revises: 1979b0b07d2a
Create Date: 2026-06-15 03:29:39.674273

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7ca4cd2460d0'
down_revision: Union[str, None] = '1979b0b07d2a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
