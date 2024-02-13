"""Agrego roles a la tabla roles

Revision ID: bd9e17f99ea8
Revises: 3aa14f4ce0e9
Create Date: 2024-02-13 12:32:30.947362

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bd9e17f99ea8'
down_revision: Union[str, None] = '3aa14f4ce0e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    roles_estaticos_dict = [
        {
            'nombre_corto': 'ADMIN',
            'nombre_largo': 'Administrador'
        },
        {
            'nombre_corto': 'CAJERO',
            'nombre_largo': 'Cajero'
        },
        {
            'nombre_corto': 'TAPERO',
            'nombre_largo': 'Tapero'
        },
        {
            'nombre_corto': 'CLIENTE_ESTANDAR',
            'nombre_largo': 'Cliente Estandar'
        },
        {
            'nombre_corto': 'CLIENTE_VIP',
            'nombre_largo': 'Cliente VIP'
        },
    ]

    for rol_estatico in roles_estaticos_dict:
        op.execute(f"""
                INSERT INTO roles (nombre_corto, nombre_largo) 
                VALUES ('{rol_estatico['nombre_corto']}', '{rol_estatico['nombre_largo']}') 
                ON CONFLICT (nombre_corto) DO NOTHING;
            """
        )
        # op.execute(f"INSERT INTO roles (nombre_corto, nombre_largo) VALUES ({rol_estatico['nombre_corto']}, {rol_estatico['nombre_largo']}) ON CONFLICT (nombre_corto) DO NOTHING;")
        


def downgrade() -> None:
    pass
