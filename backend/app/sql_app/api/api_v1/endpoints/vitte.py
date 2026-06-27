from fastapi import APIRouter

from sql_app.api.vitte_integration.vitte_service import vitte_service
from sql_app.api.vitte_integration.vitte_utils import vitte_api_client
from sql_app.api.vitte_integration.vitte_schemas import VitteStatus

router = APIRouter()


@router.get("/status", response_model=VitteStatus)
def handle_read_vitte_status() -> VitteStatus:
    return vitte_service.get_status(vitte_api_client.check_health)
