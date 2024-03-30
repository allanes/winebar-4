# backend/app/sql_app/schemas/validators.py

from typing import Union, Dict, Any
from sqlalchemy.orm import Session
from sql_app.api import deps
from sql_app.models.tarjetas_y_usuarios import PersonalInterno
import json

def clean_tarjeta_id(value: Union[int, str]) -> int:
    if isinstance(value, int):
        return value

    cleaned_value = value.lstrip('0')
    try:
        return int(cleaned_value) if cleaned_value else None
    except ValueError:
        raise ValueError(f"Tarjeta no válida: {value}")
