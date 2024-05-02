# backend/app/sql_app/schemas/validators.py

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Union, Dict, Any
from sqlalchemy.orm import Session
# from sql_app.api import deps
# from sql_app.models.tarjetas_y_usuarios import PersonalInterno
import json

def clean_tarjeta_id(value: Union[int, str]) -> int:
    if isinstance(value, int):
        return value

    cleaned_value = value.lstrip('0')
    try:
        return int(cleaned_value) if cleaned_value else None
    except ValueError:
        raise ValueError(f"Tarjeta no válida: {value}")

def get_now_time() -> datetime:
    ts_apertura = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))
    print(f'ts apertura extraido: {ts_apertura}')
    ts_apertura = ts_apertura.isoformat()[:26]
    ts_apertura = datetime.fromisoformat(ts_apertura)
    return ts_apertura

if __name__ == '__main__':
    print(get_now_time())