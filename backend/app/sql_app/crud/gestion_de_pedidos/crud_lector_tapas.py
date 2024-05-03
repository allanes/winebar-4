from datetime import datetime
from sqlalchemy.orm import Session
# from sql_app.crud.base_with_active import CRUDBaseWithActiveField
from sql_app.crud.base import CRUDBase
from sql_app.models.gestion_de_pedidos import LectorTapa
from sql_app.schemas.gestion_de_pedidos.lector_tapas import LectorTapaCreate, LectorTapaUpdate
from sql_app.schemas.inventario_y_promociones.producto import ProductoCreate
from sql_app import crud

class CRUDLectorTapa(CRUDBase[LectorTapa, LectorTapaCreate, LectorTapaUpdate]):    
    pass

lector_tapa = CRUDLectorTapa(LectorTapa)