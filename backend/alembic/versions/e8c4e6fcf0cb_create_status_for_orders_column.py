"""Create status for orders column

Revision ID: e8c4e6fcf0cb
Revises: 
Create Date: 2026-01-10 13:01:03.179244

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e8c4e6fcf0cb'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('orders', sa.Column('status', sa.String(), nullable=False, server_default="Placed"))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('orders', 'status')
