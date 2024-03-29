# backend/app/sql_app/schemas/validators.py

from typing import Union, Dict, Any
from sqlalchemy.orm import Session
from sql_app.api import deps
from sql_app.models.tarjetas_y_usuarios import PersonalInterno
from sql_app.models.gestion_de_pedidos import OrdenCompra
from sql_app import crud
import json

def __get_internal_db_session():
    db: Session = deps.get_db()
    db_session = next(db)
    # yield db_session
    # db_session.close()
    return db_session

def serializer_for_nombre_personal(atendido_por_id: int) -> str:
    # db_session = __get_internal_db_session()
    db: Session = deps.get_db()
    db_session = next(db)
    
    nombre_completo = crud.personal_interno.armar_nombre_completo(
        db=db_session,
        personal_id=atendido_por_id
    )

    db.close()
    return nombre_completo

def serializer_for_suma_ordenes_para_turno(turno_id: int) -> float:
    # db_session = __get_internal_db_session()
    db: Session = deps.get_db()
    db_session = next(db)
    
    monto_cobrado_de_ordenes = crud.turno.get_suma_cobrada_de_ordenes(
        db=db_session, turno_id=turno_id
    )
    
    db.close()
    return monto_cobrado_de_ordenes

def serializer_for_clientes_activos(turno_id: int) -> int:
    # db_session = __get_internal_db_session()
    db: Session = deps.get_db()
    db_session = next(db)

    ordenes_in_db = crud.orden.get_by_turno_id(
        db=db_session,
        turno_id=turno_id
    )

    ordenes_activas = [orden for orden in ordenes_in_db if orden.cerrada_por is None]

    db.close()
    return len(ordenes_activas)

def serializer_for_clientes_totales(turno_id: int) -> int:
    # db_session = __get_internal_db_session()
    db: Session = deps.get_db()
    db_session = next(db)

    ordenes_in_db = crud.orden.get_by_turno_id(
        db=db_session,
        turno_id=turno_id
    )
    
    db.close()
    return len(ordenes_in_db)
