"""empty message

Revision ID: 3aa14f4ce0e9
Revises: eac371e94226
Create Date: 2024-02-13 03:11:29.435613

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3aa14f4ce0e9'
down_revision: Union[str, None] = '240abe5a681d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('configuraciones',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('monto_maximo_orden_def', sa.Float(), nullable=False),
    sa.Column('monto_maximo_pedido_def', sa.Float(), nullable=False),
    sa.Column('fecha_ultima_actualizacion', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('menues',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('promociones',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('descuento', sa.Float(), nullable=False),
    sa.Column('vigencia_desde', sa.DateTime(), nullable=False),
    sa.Column('vigencia_hasta', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('productos',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('titulo', sa.String(), nullable=False),
    sa.Column('descripcion', sa.String(), nullable=True),
    sa.Column('precio', sa.Float(), nullable=False),
    sa.Column('ultimo_cambio_precio', sa.DateTime(), nullable=False),
    sa.Column('activo', sa.Boolean(), nullable=True),
    sa.Column('stock', sa.Integer(), nullable=False),
    sa.Column('id_menu', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id_menu'], ['menues.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('turnos',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('timestamp_apertura', sa.DateTime(), nullable=False),
    sa.Column('timestamp_cierre', sa.DateTime(), nullable=True),
    sa.Column('cantidad_de_ordenes', sa.Integer(), nullable=False),
    sa.Column('cantidad_tapas', sa.Integer(), nullable=False),
    sa.Column('cantidad_usuarios_vip', sa.Integer(), nullable=False),
    sa.Column('ingresos_totales', sa.Float(), nullable=False),
    sa.Column('abierto_por', sa.Integer(), nullable=False),
    sa.Column('cerrado_por', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['abierto_por'], ['personal_interno.id'], ),
    sa.ForeignKeyConstraint(['cerrado_por'], ['personal_interno.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ordenes',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('precarga_usada', sa.Float(), nullable=False),
    sa.Column('monto_cobrado', sa.Float(), nullable=False),
    sa.Column('monto_maximo_orden', sa.Float(), nullable=False),
    sa.Column('timestamp_apertura_orden', sa.DateTime(), nullable=False),
    sa.Column('timestamp_cierre_orden', sa.DateTime(), nullable=True),
    sa.Column('turno_id', sa.Integer(), nullable=True),
    sa.Column('cliente_id', sa.Integer(), nullable=True),
    sa.Column('abierta_por', sa.Integer(), nullable=True),
    sa.Column('cerrada_por', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['abierta_por'], ['personal_interno.id'], ),
    sa.ForeignKeyConstraint(['cerrada_por'], ['personal_interno.id'], ),
    sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id'], ),
    sa.ForeignKeyConstraint(['turno_id'], ['turnos.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('productos_y_promociones',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('id_producto', sa.Integer(), nullable=True),
    sa.Column('id_promocion', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id_producto'], ['productos.id'], ),
    sa.ForeignKeyConstraint(['id_promocion'], ['promociones.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tapas',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('id_producto', sa.Integer(), nullable=True),
    sa.Column('foto', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['id_producto'], ['productos.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tragos',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('id_producto', sa.Integer(), nullable=True),
    sa.Column('foto', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['id_producto'], ['productos.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('vinos',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('id_producto', sa.Integer(), nullable=True),
    sa.Column('listado_nombres', sa.String(), nullable=False),
    sa.Column('listado_precios_sugeridos', sa.String(), nullable=False),
    sa.Column('listado_metadatos', sa.String(), nullable=False),
    sa.Column('ultima_sincronizacion', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['id_producto'], ['productos.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('pedidos',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('timestamp_pedido', sa.DateTime(), nullable=False),
    sa.Column('monto_maximo_pedido', sa.Float(), nullable=False),
    sa.Column('promocion_aplicada', sa.Boolean(), nullable=True),
    sa.Column('orden_id', sa.Integer(), nullable=True),
    sa.Column('atendido_por', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['atendido_por'], ['personal_interno.id'], ),
    sa.ForeignKeyConstraint(['orden_id'], ['ordenes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('renglones',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('cantidad', sa.Integer(), nullable=False),
    sa.Column('monto', sa.Float(), nullable=False),
    sa.Column('pedido_id', sa.Integer(), nullable=True),
    sa.Column('producto_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['pedido_id'], ['pedidos.id'], ),
    sa.ForeignKeyConstraint(['producto_id'], ['productos.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('renglones')
    op.drop_table('pedidos')
    op.drop_table('vinos')
    op.drop_table('tragos')
    op.drop_table('tapas')
    op.drop_table('productos_y_promociones')
    op.drop_table('ordenes')
    op.drop_table('turnos')
    op.drop_table('productos')
    op.drop_table('promociones')
    op.drop_table('menues')
    op.drop_table('configuraciones')
    # ### end Alembic commands ###