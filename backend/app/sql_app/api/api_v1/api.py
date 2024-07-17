from fastapi import APIRouter

from sql_app.api.api_v1.endpoints.tarjetas_y_usuarios import roles, tarjetas, personal_internos, clientes
from sql_app.api.api_v1.endpoints.inventario_y_promociones import tapas, vinos
from sql_app.api.api_v1.endpoints.gestion_de_pedidos import turnos, ordenes, pedidos, lectores_tapas, configuraciones
from sql_app.api.api_v1.endpoints import login
from sql_app.api.fudo_integration import fudo_router

api_router = APIRouter()
api_router.include_router(login.router, prefix='/login', tags=["login"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
api_router.include_router(tarjetas.router, prefix="/tarjetas", tags=["Tarjetas"])
api_router.include_router(personal_internos.router, prefix="/personal", tags=["Personal Interno"])
api_router.include_router(clientes.router, prefix="/clientes", tags=["Clientes"])
api_router.include_router(tapas.router, prefix="/tapas", tags=["Tapas"])
api_router.include_router(turnos.router, prefix="/turnos", tags=["Turnos"])
api_router.include_router(ordenes.router, prefix="/ordenes", tags=["Ordenes"])
api_router.include_router(pedidos.router, prefix="/pedidos", tags=["Pedidos"])
api_router.include_router(vinos.router, prefix="/vinos", tags=["Vinos"])
api_router.include_router(fudo_router.router, prefix="/fudo", tags=["Fudo"])
api_router.include_router(lectores_tapas.router, prefix="/lectores-tapas", tags=["Lectores de Tapas"])
api_router.include_router(configuraciones.router, prefix="/configuraciones", tags=["Configuracion"])

tags_metadata = [
    # {
    #     "name": "items",
    #     "description": "Manage items. So _fancy_ they have their own docs.",
    #     "externalDocs": {
    #         "description": "Items external docs",
    #         "url": "https://fastapi.tiangolo.com/",
    #     },
    # },
    {
        "name": "login",
        "description": ""
    },
    {
        "name": "Tarjetas",
        "description": ""
    },
    {
        "name": "Personal Interno",
        "description": ""
    },
    {
        "name": "Clientes",
        "description": ""
    },
    {
        "name": "Tapas",
        "description": ""
    },
    {
        "name": "Turnos",
        "description": ""
    },
    {
        "name": "Ordenes",
        "description": ""
    },
    {
        "name": "Pedidos",
        "description": ""
    },
]