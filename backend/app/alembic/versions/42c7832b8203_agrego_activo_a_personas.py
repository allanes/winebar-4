"""Agrego activo a personas

Revision ID: 42c7832b8203
Revises: bd9e17f99ea8
Create Date: 2024-02-13 16:29:33.826970

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '42c7832b8203'
down_revision: Union[str, None] = 'bd9e17f99ea8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('clientes', sa.Column('activo', sa.Boolean(), nullable=False))
    op.add_column('personal_interno', sa.Column('activo', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('personal_interno', 'activo')
    op.drop_column('clientes', 'activo')
    # ### end Alembic commands ###