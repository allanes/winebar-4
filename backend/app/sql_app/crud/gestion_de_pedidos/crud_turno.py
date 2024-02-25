from datetime import datetime
from sqlalchemy.orm import Session
# from sql_app.crud.base_with_active import CRUDBaseWithActiveField
from sql_app.crud.base import CRUDBase
from sql_app.models.gestion_de_pedidos import Turno
from sql_app.schemas.gestion_de_pedidos.turno import TurnoCreate, TurnoUpdate
from sql_app.schemas.inventario_y_promociones.producto import ProductoCreate
from sql_app import crud

class CRUDTurno(CRUDBase[Turno, TurnoCreate, TurnoUpdate]):    
    def abrir_turno(self, db: Session, *, turno_in: TurnoCreate) -> Turno:
        turno_in_db = Turno()
        
        turno_in_db.timestamp_apertura = datetime.now()
        turno_in_db.cantidad_de_ordenes = -1
        turno_in_db.cantidad_tapas = -1
        turno_in_db.cantidad_usuarios_vip = -1
        turno_in_db.ingresos_totales = -1
        turno_in_db.abierto_por = turno_in.abierto_por

        turno_in_db = super().create(db=db, obj_in=turno_in_db)
        
        return turno_in_db
    
    def cerrar_turno(self, db: Session, *, cerrado_por: int) -> Turno:
        turno_in_db = self.get_open_turno(db=db)

        turno_in_db.cerrado_por = cerrado_por
        turno_in_db.timestamp_cierre = datetime.now()
        turno_in_db.cantidad_de_ordenes = 0
        turno_in_db.cantidad_tapas = 0
        turno_in_db.cantidad_usuarios_vip = 0
        turno_in_db.ingresos_totales = 0

        db.commit()
        db.refresh(turno_in_db)
        
        return turno_in_db
    
    def get_open_turno(self, db: Session) -> Turno:
        return db.query(Turno).order_by(Turno.id.desc()).first()


turno = CRUDTurno(Turno)