from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import List
from sqlalchemy.orm import Session
# from sql_app.crud.base_with_active import CRUDBaseWithActiveField
from sql_app.crud.base import CRUDBase
from sql_app.models.gestion_de_pedidos import Turno, OrdenCompra
from sql_app.schemas.gestion_de_pedidos.turno import TurnoCreate, TurnoUpdate, Turno as TurnoSchema, InfoDeCierre
from sql_app.schemas.inventario_y_promociones.producto import ProductoCreate
from sql_app import crud
from sql_app.schemas.validators import get_now_time

class CRUDTurno(CRUDBase[Turno, TurnoCreate, TurnoUpdate]):    
    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Turno]:
        turnos = db.query(Turno)
        turnos = turnos.order_by(Turno.id.desc())
        turnos = turnos.order_by(Turno.cerrado_por.is_(None).asc())
        turnos = turnos.offset(skip)
        turnos = turnos.limit(limit)
        turnos = turnos.all()
        return turnos
    
    def abrir_turno(self, db: Session, *, turno_in: TurnoCreate) -> Turno:
        ts_apertura = get_now_time()
        turno_in_db = Turno()
        turno_in_db.timestamp_apertura = ts_apertura
        turno_in_db.cantidad_de_ordenes = -1
        turno_in_db.cantidad_tapas = -1
        turno_in_db.cantidad_usuarios_vip = -1
        turno_in_db.monto_en_caja = 0
        turno_in_db.abierto_por = turno_in.abierto_por

        turno_in_db = super().create(db=db, obj_in=turno_in_db)
        
        return turno_in_db
    
    def cerrar_turno(
            self, db: Session, *, cerrado_por: int, info_de_cierre: InfoDeCierre
        ) -> tuple[Turno | None, bool, str]:
        turno_in_db = self.get_open_turno(db=db)
        if turno_in_db is None:
            return None, False, 'No se encontró un turno abierto.'

        cant_ordenes_abiertas = self.obtener_cantidad_ordenes_abiertas(
            db=db,
            turno_id=turno_in_db.id
        )
        if cant_ordenes_abiertas != 0:
            return None, False, f'Todavía existen {cant_ordenes_abiertas} clientes activos. Debe cerrar todas las ordenes abiertas antes de cerrar la caja.'
        
        cant_total_ordenes = len(crud.orden.get_by_turno_id(
            db = db, turno_id = turno_in_db.id
        ))
        ts_cierre = get_now_time()

        turno_in_db.cerrado_por = cerrado_por
        turno_in_db.timestamp_cierre = ts_cierre
        turno_in_db.cantidad_de_ordenes = cant_total_ordenes
        turno_in_db.cantidad_tapas = 0
        turno_in_db.cantidad_usuarios_vip = 0
        turno_in_db.monto_en_caja = info_de_cierre.monto_en_caja
        turno_in_db.comentarios = info_de_cierre.comentarios

        db.commit()
        db.refresh(turno_in_db)

        ## Chequeo que no haya quedado usuario operando y limpio
        clientes_operan_del_turno = crud.cliente_opera_con_tarjeta.get_multi(db=db)
        for cliente_ingresado in clientes_operan_del_turno:
            tarjeta = crud.tarjeta.get_active(db=db, id=cliente_ingresado.tarjeta_id)
            if tarjeta is not None:
                if tarjeta.presente_en_salon:
                    print(f'ADVERTENCIA. TURNO CERRADO CON TARJETA {tarjeta.id} PARA CLIENTE {cliente_ingresado.id_cliente}')
                    crud.cliente.devolver_tarjeta_de_cliente(db=db, id=cliente_ingresado.id)
                
            ## Limpio clientes operan
            cliente_opera_removido = crud.cliente_opera_con_tarjeta.remove(db=db, id=cliente_ingresado.id)
            if not cliente_opera_removido:
                print(f'Cliente {cliente_ingresado.id} no se pudo remover')
            else:
                print(f'Cliente {cliente_ingresado.id} REMOVIDO')
        
        return turno_in_db, True, ''
    
    def get_open_turno(self, db: Session) -> Turno | None:
        opened = db.query(Turno).filter(Turno.cerrado_por == None).first()
        if opened:
            print(f'Turno abierto encontrado id: {opened.id}')
        return opened
    
    def get_suma_cobrada_de_ordenes(self, db: Session, turno_id: int) -> float:
        ordenes_del_turno_in_db = crud.orden.get_by_turno_id(db=db, turno_id=turno_id)
        ordenes_del_turno_in_db: list[OrdenCompra]

        montos_cobrados = [orden.monto_cobrado for orden in ordenes_del_turno_in_db if orden.monto_cobrado >= 0]
        monto_cobrado_de_ordenes = sum(montos_cobrados)

        return monto_cobrado_de_ordenes
    
    def obtener_cantidad_ordenes_abiertas(self, db: Session, turno_id: int) -> int:
        turno_abierto = self.get_open_turno(db=db)
        if not turno_abierto: 
            return []
        
        ordenes_de_turno_actual = crud.orden.get_by_turno_id(
            db=db, turno_id=turno_id
        )
        ordenes_activas = [orden for orden in ordenes_de_turno_actual if orden.cerrada_por is None]
        return len(ordenes_activas)

turno = CRUDTurno(Turno)