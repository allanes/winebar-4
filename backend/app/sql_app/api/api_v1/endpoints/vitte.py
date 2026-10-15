from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from sql_app import crud
from sql_app.api import deps
from sql_app.api.vitte_integration.vitte_service import vitte_service
from sql_app.api.vitte_integration.vitte_utils import vitte_api_client
from sql_app.api.vitte_integration.vitte_schemas import VitteStatus

router = APIRouter()


@router.get("/status", response_model=VitteStatus)
def handle_read_vitte_status(db: Session = Depends(deps.get_db)) -> VitteStatus:
    status = vitte_service.get_status(vitte_api_client.check_health)
    if status.online:
        # Con conexion, se regulariza lo que quedo pendiente mientras Vitte no estaba disponible:
        # descuentos de tapas sobre el saldo y tarjetas de ordenes ya cerradas
        crud.cliente.aplicar_descuentos_pendientes(db=db)
        crud.cliente.liberar_tarjetas_pendientes(db=db)
    return status
