import os
from typing import Dict, Any, List

from sqlalchemy.orm import Session
# from sql_app.crud.base_with_active import CRUDBaseWithActiveField
from sql_app.models.inventario_y_promociones import Vino, Producto as ProductoModel
from sql_app.models.gestion_de_pedidos import Renglon as RenglonModel
from sql_app.schemas.inventario_y_promociones.vino import VinoCreate, VinoUpdate
from sql_app.schemas.inventario_y_promociones.producto import ProductoCreate, ProductoUpdate
from sql_app.api.vitte_integration.vitte_utils import vitte_api_client
from sql_app.api.vitte_integration.vitte_schemas import PicoDeModulo
from sql_app.crud.base import CRUDBase
from sql_app import crud
from sql_app import schemas

class CRUDVino(CRUDBase[Vino, VinoCreate, VinoUpdate]):
    def remove(self, db: Session, *, id: int) -> Vino:
        vino_in_db = self.get(db=db, id=id)
        if vino_in_db is None: return None
        producto_id = vino_in_db.id_producto
        producto_removido, pudo_removerse, msg = crud.producto.deactivate(db=db, id=producto_id)
        vino_removida = super().remove(db, id=id)
        
        return vino_removida
    
    def update(self, db: Session, *, db_obj: Vino, obj_in: VinoUpdate | Dict[str, Any]) -> Vino:
        producto_actualizado_in_db = crud.producto.update(db=db, db_obj=db_obj.producto, obj_in=obj_in)
        
        db_obj.id_producto = producto_actualizado_in_db.id
        db.commit()
        db.refresh(db_obj)

        return db_obj
    
    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Vino]:
        return db.query(Vino).order_by(Vino.id).offset(skip).limit(limit).all()

    def get_by_product_id(self, db: Session, producto_id: int) -> Vino | None:
        vino_in_db = db.query(Vino)
        vino_in_db = vino_in_db.filter(Vino.id_producto == producto_id)
        vino_in_db = vino_in_db.first()
        return vino_in_db
    
    def get_by_vitte_name(self, db: Session, vitte_name: str, tamaño_copa: float) -> Vino | None:
        print(f'buscando vino por nombre y tam: {vitte_name}, {tamaño_copa}')
        productos_in_db = db.query(ProductoModel).filter(ProductoModel.titulo == vitte_name).all()

        if not productos_in_db:
            return None
        
        vinos_in_db = db.query(Vino).filter(Vino.id_producto.in_([producto.id for producto in productos_in_db]))
        vino_in_db = vinos_in_db.filter(Vino.volumen == tamaño_copa).first()

        return vino_in_db

vino = CRUDVino(Vino)