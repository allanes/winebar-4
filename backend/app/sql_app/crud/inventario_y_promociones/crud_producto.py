from datetime import datetime
from sqlalchemy.orm import Session
from sql_app.crud.base_with_active import CRUDBaseWithActiveField
from sql_app.models.inventario_y_promociones import Producto
from sql_app.schemas.inventario_y_promociones.producto import ProductoCreate, ProductoUpdate

class CRUDProducto(CRUDBaseWithActiveField[Producto, ProductoCreate, ProductoUpdate]):
    ### Functions override section
    def apply_activation_defaults(self, obj_in: ProductoCreate | ProductoUpdate, db_obj: Producto, db: Session = None) -> Producto:
        # return super().apply_activation_defaults(obj_in, db_obj, db)
        producto_in = obj_in
        producto_in_db = db_obj

        [setattr(producto_in_db, attr, value) for attr, value in producto_in.model_dump().items()]
        producto_in_db.activa = True
        producto_in_db.ultimo_cambio_precio = datetime.now()
        producto_in_db.id_menu = 1
        producto_in_db.tapa = None
        producto_in_db.vino = None
        producto_in_db.trago = None
        if producto_in.stock is None:
            producto_in_db.stock = 0

        return producto_in_db
            

    def create_or_reactivate(self, db: Session, *, obj_in: ProductoCreate, custom_id_field: str = 'id') -> tuple[Producto | None, bool, str]:
        # Have to create
        check_passed, message = self.pre_create_checks(
            db=db,
            obj_in=obj_in
        )
        if not check_passed:
            return None, False, message
            
        created_obj = self.create(db=db, obj_in=obj_in)
        return created_obj, True, ""  # Successful creation
    ### End of Functions override section
    
    
    pass

producto = CRUDProducto(Producto)