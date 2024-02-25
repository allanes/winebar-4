from datetime import datetime
from sqlalchemy.orm import Session
# from sql_app.crud.base_with_active import CRUDBaseWithActiveField
from sql_app.crud.base import CRUDBase
from sql_app.models.gestion_de_pedidos import Turno
from sql_app.schemas.gestion_de_pedidos.turno import TurnoCreate, TurnoUpdate
from sql_app.schemas.inventario_y_promociones.producto import ProductoCreate
from sql_app import crud

class CRUDTurno(CRUDBase[Turno, TurnoCreate, TurnoUpdate]):
    def create(self, db: Session, *, obj_in: TurnoCreate) -> Turno:
        # obj_in_data = jsonable_encoder(obj_in)
        # db_obj = self.model(**obj_in_data)  # type: ignore
        
        turno_in_db = Turno()
        turno_in_db.timestamp_apertura = datetime.now()
        turno_in_db.cantidad_de_ordenes = -1
        turno_in_db.cantidad_tapas = -1
        turno_in_db.cantidad_usuarios_vip = -1
        turno_in_db.ingresos_totales = -1
        turno_in_db.abierto_por = obj_in.abierto_por
        
        db.add(turno_in_db)
        db.commit()
        db.refresh(turno_in_db)
        return turno_in_db
    
    def remove(self, db: Session, *, id: int) -> Turno:
        tapa_in_db = self.get(db=db, id=id)
        if tapa_in_db is None: return None
        producto_id = tapa_in_db.id_producto
        producto_removido, pudo_removerse, msg = crud.producto.deactivate(db=db, id=producto_id)
        tapa_removida = super().remove(db, id=id)
        
        return tapa_removida


turno = CRUDTurno(Turno)