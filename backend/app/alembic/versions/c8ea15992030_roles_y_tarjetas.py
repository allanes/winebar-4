"""Roles y tarjetas

Revision ID: c8ea15992030
Revises: 
Create Date: 2024-02-12 22:23:21.804884

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c8ea15992030'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('roles',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('nombre_corto', sa.String(), nullable=False),
    sa.Column('nombre_largo', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('nombre_corto'),
    sa.UniqueConstraint('nombre_largo')
    )
    op.create_table('tarjetas',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('raw_rfid', sa.String(), nullable=False),
    sa.Column('activa', sa.Boolean(), nullable=True),
    sa.Column('fecha_alta', sa.DateTime(), nullable=True),
    sa.Column('fecha_ultimo_uso', sa.DateTime(), nullable=True),
    sa.Column('entregada', sa.Boolean(), nullable=True),
    sa.Column('presente_en_salon', sa.Boolean(), nullable=True),
    sa.Column('monto_precargado', sa.Float(), nullable=True),
    sa.Column('rol_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['rol_id'], ['roles.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tarjetas')
    op.drop_table('roles')
    # ### end Alembic commands ###
