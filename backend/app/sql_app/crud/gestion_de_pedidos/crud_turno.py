from datetime import datetime
from sqlalchemy.orm import Session
# from sql_app.crud.base_with_active import CRUDBaseWithActiveField
from sql_app.crud.base import CRUDBase
from sql_app.models.gestion_de_pedidos import Turno, OrdenCompra
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
    
    def cerrar_turno(self, db: Session, *, cerrado_por: int) -> Turno | None:
        turno_in_db = self.get_open_turno(db=db)
        if turno_in_db is None:
            return None

        turno_in_db.cerrado_por = cerrado_por
        turno_in_db.timestamp_cierre = datetime.now()
        turno_in_db.cantidad_de_ordenes = 0
        turno_in_db.cantidad_tapas = 0
        turno_in_db.cantidad_usuarios_vip = 0
        turno_in_db.ingresos_totales = 0

        db.commit()
        db.refresh(turno_in_db)
        
        return turno_in_db
    
    def get_open_turno(self, db: Session) -> Turno | None:
        turno = db.query(Turno).order_by(Turno.id.desc()).first()
        if not turno:
            return None
        
        # Cantidad de ordenes
        ## Metodo 1
        clientes_operan = crud.cliente_opera_con_tarjeta.get_multi(db=db)
        cantidad_ordenes_desde_cliente_opera = len(clientes_operan)
        ## Metodo 2
        ordenes_del_turno = db.query(OrdenCompra)
        ordenes_del_turno = ordenes_del_turno.filter(OrdenCompra.turno_id == turno.id)
        ordenes_del_turno = ordenes_del_turno.all()
        cantidad_ordenes_desde_ordenes = len(ordenes_del_turno)
        ## 
        print(f'cantidad_ordenes_desde_cliente_opera: {cantidad_ordenes_desde_cliente_opera}')
        print(f'cantidad_ordenes_desde_ordenes: {cantidad_ordenes_desde_ordenes}')
        ## ---
        
        # Cantidad de tapas
        

        # Pongo todos los datos en el turno actual
        turno.cantidad_de_ordenes = cantidad_ordenes_desde_cliente_opera
        # turno.cantidad_tapas = cantidad_tapas

        return turno


turno = CRUDTurno(Turno)