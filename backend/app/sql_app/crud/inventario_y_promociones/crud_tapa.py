import os
from typing import Dict, Any
from sqlalchemy.orm import Session
# from sql_app.crud.base_with_active import CRUDBaseWithActiveField
from sql_app.crud.base import CRUDBase
from sql_app.models.inventario_y_promociones import Tapa
from sql_app.schemas.inventario_y_promociones.tapa import TapaCreate, TapaUpdate, TapaConProductoCreate
from sql_app.schemas.inventario_y_promociones.producto import ProductoCreate, ProductoUpdate
from sql_app import crud

class CRUDTapa(CRUDBase[Tapa, TapaCreate, TapaUpdate]):
    def create_with_producto_data(
            self, db: Session, tapa_con_producto_in: TapaConProductoCreate
        ) -> tuple[Tapa | None, bool, str]:
        producto_in = ProductoCreate(**tapa_con_producto_in.model_dump())
        
        producto_in_db, fue_creado, msg = crud.producto.create_or_reactivate(
            db=db, obj_in=producto_in)
        if not fue_creado:
            return None, fue_creado, msg
        
        tapa_in = TapaCreate(
            id_producto=producto_in_db.id,
        )

        tapa_in_db = self.create(db=db, obj_in=tapa_in)

        if tapa_in_db is None:
            return None, False, 'La tapa no se pudo crear'

        return tapa_in_db, True, ''
    
    def remove(self, db: Session, *, id: int) -> Tapa:
        tapa_in_db = self.get(db=db, id=id)
        if tapa_in_db is None: return None
        producto_id = tapa_in_db.id_producto
        producto_removido, pudo_removerse, msg = crud.producto.deactivate(db=db, id=producto_id)
        tapa_removida = super().remove(db, id=id)
        
        return tapa_removida
    
    def get_tapa_image_name(self, tapa_in_db: Tapa) -> str:
        cadena = f"tapa_{tapa_in_db.id}.jpg"
        return cadena
    
    def update(self, db: Session, *, db_obj: Tapa, obj_in: TapaUpdate | Dict[str, Any]) -> Tapa:
        producto_actualizado_in_db = crud.producto.update(db=db, db_obj=db_obj.producto, obj_in=obj_in)
        
        db_obj.id_producto = producto_actualizado_in_db.id
        db.commit()
        db.refresh(db_obj)

        return db_obj


tapa = CRUDTapa(Tapa)