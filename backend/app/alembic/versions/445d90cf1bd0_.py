"""empty message

Revision ID: 445d90cf1bd0
Revises: 029ebbf4632f
Create Date: 2024-02-25 16:33:44.383411

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '445d90cf1bd0'
down_revision: Union[str, None] = '029ebbf4632f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('configuraciones', sa.Column('vitte_listado_nombres', sa.String(), nullable=False))
    op.add_column('configuraciones', sa.Column('vitte_listado_precios_sugeridos', sa.String(), nullable=False))
    op.add_column('configuraciones', sa.Column('vitte_listado_metadatos', sa.String(), nullable=False))
    op.add_column('configuraciones', sa.Column('vitte_ultima_sincronizacion', sa.DateTime(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('configuraciones', 'vitte_ultima_sincronizacion')
    op.drop_column('configuraciones', 'vitte_listado_metadatos')
    op.drop_column('configuraciones', 'vitte_listado_precios_sugeridos')
    op.drop_column('configuraciones', 'vitte_listado_nombres')
    # ### end Alembic commands ###