"""empty message

Revision ID: 22d361e30f54
Revises: 36e7db46377d
Create Date: 2024-02-22 23:27:03.660710

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '22d361e30f54'
down_revision: Union[str, None] = '36e7db46377d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('clientes_y_tarjetas', 'tarjeta', new_column_name='tarjeta_id', existing_type=sa.Integer())
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('clientes_y_tarjetas', 'tarjeta_id', new_column_name='tarjeta', existing_type=sa.Integer())
    # ### end Alembic commands ###
