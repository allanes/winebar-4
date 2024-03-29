from datetime import datetime
from sqlalchemy.orm import Session
# from sql_app.crud.base_with_active import CRUDBaseWithActiveField
from sql_app.crud.base import CRUDBase
from sql_app.models.gestion_de_pedidos import Turno, OrdenCompra
from sql_app.schemas.gestion_de_pedidos.turno import TurnoCreate, TurnoUpdate, Turno as TurnoSchema, InfoDeCierre
from sql_app.schemas.inventario_y_promociones.producto import ProductoCreate
from sql_app import crud

class CRUDTurno(CRUDBase[Turno, TurnoCreate, TurnoUpdate]):    
    def abrir_turno(self, db: Session, *, turno_in: TurnoCreate) -> Turno:
        turno_in_db = Turno()
        
        turno_in_db.timestamp_apertura = datetime.now()
        turno_in_db.cantidad_de_ordenes = -1
        turno_in_db.cantidad_tapas = -1
        turno_in_db.cantidad_usuarios_vip = -1
        turno_in_db.monto_en_caja = -1
        turno_in_db.abierto_por = turno_in.abierto_por

        turno_in_db = super().create(db=db, obj_in=turno_in_db)
        
        return turno_in_db
    
    def cerrar_turno(self, db: Session, *, cerrado_por: int, info_de_cierre: InfoDeCierre) -> Turno | None:
        turno_in_db = self.get_open_turno(db=db)
        if turno_in_db is None:
            return None

        turno_schema = self.llenar_campos_turno_en_curso(db=db, turno=turno_in_db)

        if turno_schema.clientes_activos != 0:
            return None
        
        turno_in_db.cerrado_por = cerrado_por
        turno_in_db.timestamp_cierre = datetime.now()
        turno_in_db.cantidad_de_ordenes = turno_schema.cantidad_de_ordenes
        turno_in_db.cantidad_tapas = turno_schema.cantidad_tapas
        turno_in_db.cantidad_usuarios_vip = turno_schema.cantidad_usuarios_vip
        turno_in_db.monto_en_caja = info_de_cierre.monto_en_caja
        turno_in_db.comentarios = info_de_cierre.comentarios

        db.commit()
        db.refresh(turno_in_db)
        
        return turno_in_db
    
    def get_open_turno(self, db: Session) -> Turno | None:
        opened = db.query(Turno).filter(Turno.cerrado_por == None).first()
        if opened:
            print(f'turno abierto: {opened.__dict__}')
        return opened
        
    def llenar_campos_turno_en_curso(self, db: Session, turno: Turno) -> TurnoSchema:
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

        ## Monto cobrado
        montos = [orden.monto_cobrado for orden in ordenes_del_turno]
        
        # Clientes activos
        cant_activos = len([orden for orden in ordenes_del_turno if orden.monto_cobrado == -1])

        # Pongo todos los datos en el turno actual
        turno_con_data = TurnoSchema(
            # cantidad_de_ordenes = cantidad_ordenes_desde_cliente_opera,
            clientes_activos = cant_activos,
            suma_ordenes_cobradas=sum(montos),
            **turno.__dict__            
        )

        return turno_con_data


turno = CRUDTurno(Turno)