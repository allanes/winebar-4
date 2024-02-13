import pytest
from datetime import datetime
from sql_app.schemas import TarjetaCreate, TarjetaUpdate

def test_tarjeta_create():
    # Test successful card creation with defaults
    tarjeta_data = {
        "raw_rfid": "0123456789",
        "rol_id": 1
    }
    tarjeta = TarjetaCreate(**tarjeta_data)
    assert tarjeta.raw_rfid == "0123456789"
    assert tarjeta.activa == True  # Assuming default is True
    assert tarjeta.rol_id == 1

def test_tarjeta_update_with_defaults():
    # Test updating a card with default values for optional fields
    update_data = {"monto_precargado": -1}
    tarjeta_update = TarjetaUpdate(**update_data)
    assert tarjeta_update.monto_precargado == -1