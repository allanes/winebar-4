# backend/app/sql_app/schemas/validators.py

from typing import Union, Dict, Any
from sqlalchemy.orm import Session
from sql_app.api import deps
from sql_app.models.tarjetas_y_usuarios import PersonalInterno
from sql_app.models.gestion_de_pedidos import OrdenCompra
from sql_app import crud
import json

def __get_internal_db_session() -> Session:
    db: Session = deps.get_db()
    db_session = next(db)
    return db_session

def serializer_for_nombre_personal(atendido_por_id: int) -> str:
    db_session = __get_internal_db_session()
    
    tapero_in_db = db_session.query(PersonalInterno)
    tapero_in_db = tapero_in_db.filter(PersonalInterno.id == atendido_por_id)
    tapero_in_db = tapero_in_db.filter(PersonalInterno.activa == True)
    tapero_in_db = tapero_in_db.first()
    
    nombre_completo = ''
    if tapero_in_db:
        nombre_completo = f'{tapero_in_db.nombre} {tapero_in_db.apellido}'
        
    return nombre_completo

def serializer_for_suma_ordenes_para_turno(turno_id: int) -> float:
    db_session = __get_internal_db_session()
    
    monto_cobrado_de_ordenes = crud.turno.get_suma_cobrada_de_ordenes(
        db=db_session, turno_id=turno_id
    )
    
    return monto_cobrado_de_ordenes

def serializer_for_clientes_activos(turno_id: int) -> int:
    db_session = __get_internal_db_session()

    ordenes_in_db = db_session.query(OrdenCompra)
    ordenes_in_db = ordenes_in_db.filter(OrdenCompra.cerrada_por.is_(None))
    ordenes_in_db = ordenes_in_db.filter(OrdenCompra.turno_id == turno_id)
    ordenes_in_db = ordenes_in_db.all()
    
    return len(ordenes_in_db)

def serializer_for_clientes_totales(turno_id: int) -> int:
    db_session = __get_internal_db_session()

    ordenes_in_db = db_session.query(OrdenCompra)
    ordenes_in_db = ordenes_in_db.filter(OrdenCompra.turno_id == turno_id)
    ordenes_in_db = ordenes_in_db.all()
    
    return len(ordenes_in_db)
