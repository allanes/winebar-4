from datetime import datetime
from sqlalchemy.orm import Session
# from sql_app.crud.base_with_active import CRUDBaseWithActiveField
from sql_app.crud.base import CRUDBase
from sql_app.models.gestion_de_pedidos import Pedido, Configuracion
from sql_app.schemas.gestion_de_pedidos.pedido import PedidoCreate, PedidoUpdate
from sql_app.schemas.inventario_y_promociones.producto import ProductoCreate
from sql_app.schemas.gestion_de_pedidos.renglon import RenglonCreate, RenglonCreateInternal
from sql_app import crud

class CRUDPedido(CRUDBase[Pedido, PedidoCreate, PedidoUpdate]):    
    def get_by_rfid(self, db: Session, *, tarjeta_id: int) -> list[Pedido]:
        cliente_con_tarjeta_in_db = crud.cliente_opera_con_tarjeta.get_by_tarjeta_id(db=db, tarjeta_id=tarjeta_id)
        orden_compra = crud.orden.get(db=db, id=cliente_con_tarjeta_in_db.id_cliente)
        pedidos_in_db = db.query(Pedido).filter(Pedido.orden_id == orden_compra.id).all()
        return pedidos_in_db

    def abrir_pedido(
            self, db: Session, *, pedido_in: PedidoCreate, tarjeta_cliente: int
            ) -> tuple[Pedido | None, bool, str]:
        ## Busco la orden abierta para esa tarjeta
        orden_in_db = crud.orden.get_by_rfid(db=db, tarjeta_id=tarjeta_cliente, solo_abiertas=True)
        if orden_in_db is None:
            return None, False, 'No se pudo recuperar una orden abierta para esa tarjeta'
        
        ## Reemplazar
        configuracion = Configuracion()
        configuracion.monto_maximo_orden_def = 200
        configuracion.monto_maximo_pedido_def = 100

        ## Aplico valores por defecto
        pedido_in_db = Pedido()
        pedido_in_db.timestamp_pedido = None
        pedido_in_db.cerrado = False
        pedido_in_db.orden_id = orden_in_db.id
        pedido_in_db.monto_maximo_pedido = configuracion.monto_maximo_pedido_def
        pedido_in_db.atendido_por = pedido_in.atendido_por
        
        pedido_in_db = super().create(db=db, obj_in=pedido_in_db)
        if pedido_in_db is None:
            return None, False, 'El pedido no pudo ser creado'
        
        return pedido_in_db, True, ''
    
    def cerrar_pedido(
    self, db: Session, *, cerrado_por: int, tarjeta_cliente: int
    ) -> tuple[Pedido | None, bool, str]:
        pedido_in_db = self.get_open_pedido(db=db)

        pass
        # pedido_in_db.cerrado=True

        db.commit()
        db.refresh(pedido_in_db)
        
        return pedido_in_db, True, ''
    
    def get_open_pedido(self, db: Session, orden_id: int) -> Pedido:
        pedido_in_db = db.query(Pedido)
        pedido_in_db.filter(Pedido.cerrado==False)
        pedido_in_db.filter(Pedido.orden_id == orden_id)
        pedido_in_db = pedido_in_db.first()
        # .order_by(Pedido.id.desc()).first()
        return pedido_in_db
    
    def agregar_producto_a_renglon(
        self, 
        db: Session, 
        tarjeta_cliente:int, 
        renglon_in: RenglonCreate,
        atendido_por: int,
    ) -> tuple[Pedido | None, bool, str]:
        ## Busco la orden abierta para esa tarjeta
        orden_in_db = crud.orden.get_by_rfid(db=db, tarjeta_id=tarjeta_cliente, solo_abiertas=True)
        if orden_in_db is None:
            return None, False, 'No se pudo recuperar una orden abierta para esa tarjeta'
        
        ## Busco un pedido abierto para esa orden
        pedido_in_db = self.get_open_pedido(db=db, orden_id=orden_in_db.id)
        if pedido_in_db is None:
            ## Si todavia no existe un pedido abierto, debo abrirlo
            pedido_in = PedidoCreate(atendido_por=atendido_por)
            pedido_in_db, fue_abierto, msg = self.abrir_pedido(
                db=db, 
                pedido_in=pedido_in, 
                tarjeta_cliente=tarjeta_cliente
            )

            if not fue_abierto:
                return None, False, msg
        
        print(f'pedido_recuperado: {pedido_in_db.__dict__}')
        ## Busco si tengo que crear un nuevo renglon o actualizar uno existente
        id_renglon_encontrado = None
        renglon_in_db = None

        renglones_de_orden = crud.renglon.get_by_pedido(
            db=db,
            pedido_id=pedido_in_db.id
        )
        for renglon in renglones_de_orden:
            if renglon.producto_id == renglon_in.producto_id:
                id_renglon_encontrado = renglon.id
                break

        if id_renglon_encontrado is None:
            ## Hay que crear
            renglon_in = RenglonCreateInternal(
                **renglon_in.model_dump(),
                pedido_id=pedido_in_db.id
            )
            renglon_in_db = crud.renglon.abrir_renglon(db=db, renglon_in=renglon_in)
        else:
            ## Hay que actualizar
            renglon_in_db = crud.renglon.agregar_a_renglon(
                db=db,
                id_renglon=id_renglon_encontrado,
                renglon_in=renglon_in
            )
        
        return renglon_in_db, renglon_in_db is not None, ''    

pedido = CRUDPedido(Pedido)