"""change domain in sales to string

Revision ID: dd238c9d635e
Revises: 8a0606ec516c
Create Date: 2026-01-25 18:24:01.208157

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dd238c9d635e'
down_revision: Union[str, Sequence[str], None] = '8a0606ec516c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column(
        'sales',
        'domain',
        existing_type=sa.Integer(),
        type_=sa.String(),
        nullable=False
    )



def downgrade():
    op.alter_column(
        'sales',
        'domain',
        existing_type=sa.String(),
        type_=sa.Integer(),
        nullable=False
    )
