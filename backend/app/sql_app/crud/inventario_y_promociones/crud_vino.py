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
    
    def get_by_vitte_name(
        self, db: Session, vitte_name: str, tamaño_copa: float, precio: float | None = None
    ) -> Vino | None:
        print(f'buscando vino por nombre, tam y precio: {vitte_name}, {tamaño_copa}, {precio}')
        vinos_in_db = (
            db.query(Vino)
            .join(ProductoModel, Vino.id_producto == ProductoModel.id)
            .filter(ProductoModel.titulo == vitte_name, Vino.volumen == tamaño_copa)
        )

        # En Vitte puede haber mas de un vino con el mismo nombre: primero busco el que
        # tiene el precio cobrado por Vitte, y si no hay ninguno uso el mas reciente
        if precio is not None:
            vino_in_db = vinos_in_db.filter(ProductoModel.precio == precio).order_by(Vino.id.desc()).first()
            if vino_in_db:
                return vino_in_db

        return vinos_in_db.order_by(Vino.id.desc()).first()

    def get_or_create_by_vitte_name(
        self, db: Session, vitte_name: str, tamaño_copa: float, precio: float
    ) -> Vino | None:
        vino_in_db = self.get_by_vitte_name(db=db, vitte_name=vitte_name, tamaño_copa=tamaño_copa, precio=precio)
        if vino_in_db:
            return vino_in_db

        # El vino ya no esta en un pico, o cambio el volumen de la medida en Vitte:
        # se crea con los datos del consumo para no perderlo
        print(f'Creando vino desde el consumo: {vitte_name}, {tamaño_copa}, {precio}')
        mismo_nombre = (
            db.query(Vino)
            .join(ProductoModel, Vino.id_producto == ProductoModel.id)
            .filter(ProductoModel.titulo == vitte_name, Vino.id_vitte.isnot(None))
            .order_by(Vino.id.desc())
            .first()
        )
        producto_in_db, fue_creado, msg = crud.producto.create_or_reactivate(
            db=db,
            obj_in=ProductoCreate(
                titulo=vitte_name,
                descripcion=f'Volumen: {int(tamaño_copa)} cc.',
                precio=precio,
                stock=0
            )
        )
        if not fue_creado:
            print(f'No se pudo crear el producto para {vitte_name}: {msg}')
            return None

        return self.create(db=db, obj_in=VinoCreate(
            volumen=int(tamaño_copa),
            id_vitte=mismo_nombre.id_vitte if mismo_nombre else None,
            id_producto=producto_in_db.id,
        ))

vino = CRUDVino(Vino)