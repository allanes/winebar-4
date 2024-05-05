"""empty message

Revision ID: d38397a06196
Revises: 36971ac2689d
Create Date: 2024-05-04 18:35:41.838149

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd38397a06196'
down_revision: Union[str, None] = '36971ac2689d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('configuraciones', 'vitte_ultima_sincronizacion')
    op.drop_column('configuraciones', 'vitte_listado_metadatos')
    op.drop_column('configuraciones', 'vitte_listado_precios_sugeridos')
    op.drop_column('configuraciones', 'vitte_listado_nombres')


def downgrade() -> None:
    op.add_column('configuraciones', sa.Column('vitte_listado_nombres', sa.String(), nullable=False))
    op.add_column('configuraciones', sa.Column('vitte_listado_precios_sugeridos', sa.String(), nullable=False))
    op.add_column('configuraciones', sa.Column('vitte_listado_metadatos', sa.String(), nullable=False))
    op.add_column('configuraciones', sa.Column('vitte_ultima_sincronizacion', sa.DateTime(), nullable=False))
