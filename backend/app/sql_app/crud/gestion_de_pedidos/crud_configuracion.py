import os
from typing import Dict, Any, List
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session

from sql_app.crud.base import CRUDBase
from sql_app.models.gestion_de_pedidos import Configuracion
from sql_app.schemas.gestion_de_pedidos.configuracion import ConfiguracionCreate, ConfiguracionUpdate

class CRUDConfiguracion(CRUDBase[Configuracion, ConfiguracionCreate, ConfiguracionUpdate]):
    def get_last(self, db: Session) -> Configuracion | None:
        configuracion_in_db = db.query(Configuracion)
        configuracion_in_db = configuracion_in_db.order_by(Configuracion.id.desc())
        configuracion_in_db = configuracion_in_db.first()
        return configuracion_in_db
    
    def create(self, db: Session, *, obj_in: ConfiguracionCreate) -> Configuracion:
        db_obj = Configuracion(
            **obj_in.model_dump(),
            fecha_ultima_actualizacion=datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))
        ) 
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

configuracion = CRUDConfiguracion(Configuracion)