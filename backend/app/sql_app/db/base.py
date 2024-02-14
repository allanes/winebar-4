# Import all the models, so that Base has them before being
# imported by Alembic
from sql_app.db.base_class import Base
from sql_app.models import (
# from sql_app.models.tarjetas_y_usuarios import (
    Rol,
    Tarjeta,
    Cliente,
    PersonalInterno,
    DetallesAdicionales,
    ClienteOperaConTarjeta
# # )
# # from sql_app.models.inventario_y_promociones import (
#     Menu,
#     Producto,
#     Tapa,
#     Trago,
#     Vino,
#     Promocion,
#     ProductoPromocion,
# # )
# # from sql_app.models.gestion_de_pedidos import (
#     Turno,
#     OrdenCompra,
#     Pedido,
#     Renglon,
#     Configuracion,
)
