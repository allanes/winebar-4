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
def custom_pedido_serializer(atendido_por_id: int) -> str:
    ## Armo el nombre
    db: Session = deps.get_db()
    db_session = next(db)
    tapero_in_db = db_session.query(PersonalInterno)
    tapero_in_db = tapero_in_db.filter(PersonalInterno.id == atendido_por_id)
    tapero_in_db = tapero_in_db.filter(PersonalInterno.activa == True)
    tapero_in_db = tapero_in_db.first()
    
    nombre_completo = ''
    if tapero_in_db:
        nombre_completo = f'{tapero_in_db.nombre} {tapero_in_db.apellido}'
        
    return nombre_completo