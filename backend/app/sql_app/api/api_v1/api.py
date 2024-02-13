from fastapi import APIRouter

from sql_app.api.api_v1.endpoints import roles, tarjetas, personal_internos

api_router = APIRouter()
# api_router.include_router(login.router, tags=["login"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
api_router.include_router(tarjetas.router, prefix="/tarjetas", tags=["Tarjetas"])
api_router.include_router(personal_internos.router, prefix="/personal", tags=["Personal Interno"])
