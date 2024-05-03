from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
# from sql_app.crud.base_with_active import CRUDBaseWithActiveField
from sql_app.crud.base import CRUDBase
from sql_app.models.gestion_de_pedidos import LectorTapa
from sql_app.schemas.gestion_de_pedidos.lector_tapas import LectorTapaCreate, LectorTapaUpdate
from sql_app.schemas.inventario_y_promociones.producto import ProductoCreate
from sql_app import crud

class CRUDLectorTapa(CRUDBase[LectorTapa, LectorTapaCreate, LectorTapaUpdate]):    
    def get_multi_by_terminal(self, db: Session, nombre_terminal: str) -> List[LectorTapa]:
        lectores = db.query(LectorTapa)
        lectores = lectores.filter(LectorTapa.nombre_terminal == nombre_terminal)
        lectores = lectores.all()
        return lectores
    
    def get_by_phys_name(self, db: Session, nombre_terminal: str, nombre_puerto: str) -> LectorTapa | None:
        lector = db.query(LectorTapa)
        lector = lector.filter(LectorTapa.nombre_terminal == nombre_terminal)
        lector = lector.filter(LectorTapa.nombre_puerto == nombre_puerto)
        lector = lector.first()
        return lector

lector_tapa = CRUDLectorTapa(LectorTapa)