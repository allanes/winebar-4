from datetime import datetime
from sqlalchemy.orm import Session
# from sql_app.crud.base_with_active import CRUDBaseWithActiveField
from sql_app.crud.base import CRUDBase
from sql_app.models.gestion_de_pedidos import Renglon
from sql_app.schemas.gestion_de_pedidos.renglon import RenglonCreate, RenglonUpdate, RenglonCreateInternal
from sql_app.schemas.inventario_y_promociones.producto import ProductoCreate
from sql_app import crud

class CRUDRenglon(CRUDBase[Renglon, RenglonCreate, RenglonUpdate]):    
    def abrir_renglon(self, db: Session, *, renglon_in: RenglonCreateInternal) -> Renglon:
        monto, promocion_aplicada = self.calcular_monto(db=db, renglon_in=renglon_in)
        
        renglon_in_db = Renglon(
            **renglon_in.model_dump(),
            monto = monto,
            promocion_aplicada = promocion_aplicada            
        )

        renglon_in_db = super().create(db=db, obj_in=renglon_in_db)
        
        return renglon_in_db
    
    def cerrar_renglon(self, db: Session, *, cerrado_por: int) -> Renglon:
        renglon_in_db = self.get_open_renglon(db=db)

        renglon_in_db.cerrado_por = cerrado_por
        renglon_in_db.timestamp_cierre = datetime.now()
        renglon_in_db.promocion_aplicada
        renglon_in_db.cantidad_de_ordenes = 0
        renglon_in_db.cantidad_tapas = 0
        renglon_in_db.cantidad_usuarios_vip = 0
        renglon_in_db.ingresos_totales = 0

        db.commit()
        db.refresh(renglon_in_db)
        
        return renglon_in_db
    
    # def get_open_renglon(self, db: Session) -> Renglon:
    #     return db.query(Renglon).order_by(Renglon.id.desc()).first()
    
    def get_by_pedido(self, db: Session, pedido_id: int) -> list[Renglon]:
        return db.query(Renglon).filter(Renglon.pedido_id==pedido_id).order_by(Renglon.id.asc()).all()
    
    def agregar_a_renglon(self, db: Session, id_renglon: int, renglon_in: RenglonCreate) -> Renglon:
        renglon_in_db = db.query(Renglon).filter(Renglon.id==id_renglon).first()
        renglon_in_db.cantidad += renglon_in.cantidad
        nuevo_monto, promocion_aplicada = self.calcular_monto(db=db, renglon_in=renglon_in_db)
        renglon_in_db.monto = nuevo_monto
        renglon_in_db.promocion_aplicada = promocion_aplicada
        db.commit()
        db.refresh(renglon_in_db)
        return renglon_in_db
    
    def calcular_monto(self, db: Session, renglon_in: RenglonCreateInternal) -> tuple[float, bool]:
        monto = 100
        promocion_aplicada = True

        producto_in_db = crud.producto.get(db=db, id=renglon_in.producto_id)
        if not producto_in_db: return 0, False

        monto = renglon_in.cantidad * producto_in_db.precio

        return monto, promocion_aplicada

renglon = CRUDRenglon(Renglon)