# backend/app/sql_app/schemas/validators.py

from typing import Union, Dict, Any
from sqlalchemy.orm import Session
from sql_app.api import deps
from sql_app.models.tarjetas_y_usuarios import PersonalInterno
from sql_app.models.gestion_de_pedidos import OrdenCompra
import json

def serializer_for_nombre_personal(atendido_por_id: int) -> str:
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

def serializer_for_suma_ordenes_para_turno(turno_id: int) -> float:
    ## Armo el nombre
    db: Session = deps.get_db()
    db_session = next(db)
    ordenes_in_db = db_session.query(OrdenCompra)
    ordenes_in_db = ordenes_in_db.filter(OrdenCompra.turno_id == turno_id)
    ordenes_in_db = ordenes_in_db.all()
    ordenes_in_db: list[OrdenCompra]

    montos_cobrados = [orden.monto_cobrado for orden in ordenes_in_db if orden.monto_cobrado >= 0]
    monto_cobrado_de_ordenes = sum(montos_cobrados)
    
    return monto_cobrado_de_ordenes

def serializer_for_clientes_activos(turno_id: int) -> int:
    ## Armo el nombre
    db: Session = deps.get_db()
    db_session = next(db)
    ordenes_in_db = db_session.query(OrdenCompra)
    ordenes_in_db = ordenes_in_db.filter(OrdenCompra.cerrada_por.is_(None))
    ordenes_in_db = ordenes_in_db.filter(OrdenCompra.turno_id == turno_id)
    ordenes_in_db = ordenes_in_db.all()
    
    return len(ordenes_in_db)

def serializer_for_clientes_totales(turno_id: int) -> int:
    ## Armo el nombre
    db: Session = deps.get_db()
    db_session = next(db)
    ordenes_in_db = db_session.query(OrdenCompra)
    ordenes_in_db = ordenes_in_db.filter(OrdenCompra.turno_id == turno_id)
    ordenes_in_db = ordenes_in_db.all()
    
    return len(ordenes_in_db)