from fastapi import APIRouter

from sql_app.api.api_v1.endpoints.tarjetas_y_usuarios import roles, tarjetas, personal_internos, clientes
from sql_app.api.api_v1.endpoints.inventario_y_promociones import tapas
from sql_app.api.api_v1.endpoints.gestion_de_pedidos import turnos, ordenes, pedidos

api_router = APIRouter()
# api_router.include_router(login.router, tags=["login"])
# api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
api_router.include_router(tarjetas.router, prefix="/tarjetas", tags=["Tarjetas"])
api_router.include_router(personal_internos.router, prefix="/personal", tags=["Personal Interno"])
api_router.include_router(clientes.router, prefix="/clientes", tags=["Clientes"])
api_router.include_router(tapas.router, prefix="/tapas", tags=["Tapas"])
api_router.include_router(turnos.router, prefix="/turnos", tags=["Turnos"])
api_router.include_router(ordenes.router, prefix="/ordenes", tags=["Ordenes"])
api_router.include_router(pedidos.router, prefix="/pedidos", tags=["Pedidos"])
