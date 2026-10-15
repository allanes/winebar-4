"""agrego fudo_venta_id a renglones y campos de operacion sin vitte a ordenes

Revision ID: a7c3e91f5b20
Revises: d8cf9fa75d47
Create Date: 2026-10-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7c3e91f5b20'
down_revision: Union[str, None] = 'd8cf9fa75d47'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('renglones', sa.Column('fudo_venta_id', sa.String(), nullable=True))
    op.add_column('ordenes', sa.Column('cerrada_sin_vitte', sa.Boolean(), nullable=True))
    op.add_column('ordenes', sa.Column('descuento_vitte_pendiente', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('ordenes', 'descuento_vitte_pendiente')
    op.drop_column('ordenes', 'cerrada_sin_vitte')
    op.drop_column('renglones', 'fudo_venta_id')
