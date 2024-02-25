from fastapi import APIRouter

from sql_app.api.api_v1.endpoints.tarjetas_y_usuarios import roles, tarjetas, personal_internos, clientes
from sql_app.api.api_v1.endpoints.inventario_y_promociones import tapas

api_router = APIRouter()
# api_router.include_router(login.router, tags=["login"])
# api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
api_router.include_router(tarjetas.router, prefix="/tarjetas", tags=["Tarjetas"])
api_router.include_router(personal_internos.router, prefix="/personal", tags=["Personal Interno"])
api_router.include_router(clientes.router, prefix="/clientes", tags=["Clientes"])
api_router.include_router(tapas.router, prefix="/tapas", tags=["Tapas"])
