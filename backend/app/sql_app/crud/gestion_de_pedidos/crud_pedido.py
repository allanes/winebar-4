from datetime import datetime
from sqlalchemy.orm import Session
# from sql_app.crud.base_with_active import CRUDBaseWithActiveField
from sql_app.crud.base import CRUDBase
from sql_app.models.gestion_de_pedidos import Pedido, Configuracion, OrdenCompra
from sql_app.schemas.gestion_de_pedidos.pedido import PedidoCreate, PedidoUpdate
from sql_app.schemas.inventario_y_promociones.producto import ProductoCreate
from sql_app.schemas.gestion_de_pedidos.renglon import RenglonCreate, RenglonCreateInternal
from sql_app import crud

class CRUDPedido(CRUDBase[Pedido, PedidoCreate, PedidoUpdate]):    
    def get_pedidos_por_tarjeta(self, db: Session, *, tarjeta_id: int) -> list[Pedido]:
        orden_compra = crud.orden.get_orden_abierta_by_rfid(db=db, tarjeta_id=tarjeta_id)
        if orden_compra is None: 
            return []        

        pedidos_in_db = self.get_pedidos_por_orden(db=db, orden_id=orden_compra.id)
        return pedidos_in_db
    
    def get_pedido_abierto_por_orden(self, db: Session, orden_id: int) -> Pedido | None:
        pedido_in_db = db.query(Pedido)
        pedido_in_db = pedido_in_db.filter(Pedido.cerrado==False)
        pedido_in_db = pedido_in_db.filter(Pedido.orden_id == orden_id)
        pedido_in_db = pedido_in_db.first()
        
        return pedido_in_db
    
    def get_pedidos_por_orden(self, db: Session, orden_id: int) -> list[Pedido]:
        print(f"Buscando pedidos por tarjeta para orden: {orden_id}")
        pedidos_in_db = db.query(Pedido)
        pedidos_in_db = pedidos_in_db.filter(Pedido.orden_id == orden_id)
        pedidos_in_db = pedidos_in_db.order_by(Pedido.id.asc())
        pedidos_in_db = pedidos_in_db.all()
        return pedidos_in_db
    
    def get_pedido_abierto_por_tarjeta(self, db: Session, tarjeta_id: int) -> Pedido | None:
        pedidos_for_card = self.get_pedidos_por_tarjeta(db=db, tarjeta_id=tarjeta_id)
        print(f'cant de pedidos: {len(pedidos_for_card)}')
        pedidos_abiertos = [pedido_in_db for pedido_in_db in pedidos_for_card if pedido_in_db.cerrado == False]
        
        pedido_abierto = None
        if len(pedidos_abiertos) == 0:
            return None
        elif len(pedidos_abiertos) >= 2: 
            print(f'Se encontraron {len(pedidos_abiertos)} pedidos abiertos para tarjeta {tarjeta_id}')
            pedido_abierto = pedidos_abiertos[0]
        elif len(pedidos_abiertos) == 1: 
            pedido_abierto = pedidos_abiertos[0]

        pedido_abierto_in_db = db.query(Pedido).filter(Pedido.id == pedido_abierto.id).first()
        return pedido_abierto_in_db

    def pre_apertura_checks(
        self, db: Session, *, tarjeta_cliente: int
    ) -> tuple[Pedido | None, bool, str]:
        ## Busco la orden abierta para esa tarjeta (capaz esta demas)
        orden_in_db = crud.orden.get_orden_abierta_by_rfid(db=db, tarjeta_id=tarjeta_cliente)
        if orden_in_db is None:
            return None, False, 'No se pudo recuperar una orden abierta para esa tarjeta'
        
        ## Busco si ya existia un pedido en curso
        pedido_abierto_in_db = self.get_pedido_abierto_por_orden(db=db, orden_id=orden_in_db.id)
        # pedidos_del_turno_por_tarjeta = self.get_pedidos_por_tarjeta(db=db, tarjeta_id=tarjeta_cliente)
        # if len(pedidos_del_turno_por_tarjeta) > 0:
        #     pedidos_abiertos = [pedido for pedido in pedidos_del_turno_por_tarjeta if not pedido.cerrado]
        #     if len(pedidos_abiertos) >= 1:
        #         if len(pedidos_abiertos) >= 2:
        #             print(f'Se encontraron {len(pedidos_abiertos)} pedidos abiertos para el cliente id {orden_in_db.cliente_id}')
        #         return pedidos_abiertos[-1], True, ''
        if pedido_abierto_in_db is None:
            return None, False, f'No se encontró un pedido abierto para la orden {orden_in_db.id}'
        
        return pedido_abierto_in_db, True, ''

    def abrir_pedido(
            self, db: Session, *, pedido_in: PedidoCreate, tarjeta_cliente: int
            ) -> tuple[Pedido | None, bool, str]:
        pedido_abierto, estaba_abierto, msg = self.pre_apertura_checks(db=db, tarjeta_cliente=tarjeta_cliente)
        if estaba_abierto == True:
            print(f'Devolviendo pedido que ya estaba abierto (id {pedido_abierto.id})')
            return pedido_abierto, estaba_abierto, msg
        print(f'Creando nuevo pedido')
        ## Reemplazar
        configuracion = Configuracion()
        configuracion.monto_maximo_orden_def = 200
        configuracion.monto_maximo_pedido_def = 100

        orden_de_la_tarjeta = crud.orden.get_orden_abierta_by_rfid(db=db, tarjeta_id=tarjeta_cliente)
        orden_de_la_tarjeta = orden_de_la_tarjeta.id if orden_de_la_tarjeta else None

        ## Aplico valores por defecto
        pedido_in_db = Pedido()
        pedido_in_db.timestamp_pedido = None
        pedido_in_db.cerrado = False
        pedido_in_db.orden_id = orden_de_la_tarjeta
        pedido_in_db.monto_maximo_pedido = configuracion.monto_maximo_pedido_def
        pedido_in_db.atendido_por = pedido_in.atendido_por
        
        pedido_in_db = super().create(db=db, obj_in=pedido_in_db)
        if pedido_in_db is None:
            return None, False, 'El pedido no pudo ser creado'
        
        return pedido_in_db, True, ''
    
    def cerrar_pedido(
    self, db: Session, *, cerrado_por: int, tarjeta_cliente: int
    ) -> tuple[Pedido | None, bool, str]:
        pedido_in_db = self.get_pedido_abierto_por_tarjeta(db=db, tarjeta_id=tarjeta_cliente)
        if pedido_in_db is None:
            return None, False, f'No se encontró un pedido abierto para la tarjeta {tarjeta_cliente}'

        pass
        pedido_in_db.cerrado=True
        pedido_in_db.timestamp_pedido = datetime.now()
        pedido_in_db.atendido_por = cerrado_por

        db.commit()
        db.refresh(pedido_in_db)
        
        montos_de_pedidos = [renglon.monto for renglon in pedido_in_db.renglones]
        
        crud.orden.cargar_monto(
            db=db, 
            orden_id=pedido_in_db.orden_id,
            monto_a_agregar=sum(montos_de_pedidos)
        )
        
        return pedido_in_db, True, ''
    
    def agregar_producto_a_pedido(
        self, 
        db: Session, 
        tarjeta_cliente:int, 
        renglon_in: RenglonCreate,
        atendido_por: int,
    ) -> tuple[Pedido | None, bool, str]:
        ## Busco la orden abierta para esa tarjeta
        orden_in_db = crud.orden.get_orden_abierta_by_rfid(db=db, tarjeta_id=tarjeta_cliente)
        if orden_in_db is None:
            return None, False, 'No se pudo recuperar una orden abierta para esa tarjeta'
        print(f'orden encontrada para agregar el producto: {orden_in_db.id}')
        ## Busco un pedido abierto para esa orden
        pedido_in_db = self.get_pedido_abierto_por_orden(db=db, orden_id=orden_in_db.id)
        if pedido_in_db: print(f'pedido abierto recuperado id: {pedido_in_db.id}')
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
    
    def quitar_producto_de_pedido(
        self, 
        db: Session, 
        tarjeta_cliente:int, 
        producto_id: int,
    ) -> tuple[Pedido | None, bool, str]:
        ## Mismo que self.agregar_producto()
        ## Busco la orden abierta para esa tarjeta
        orden_in_db = crud.orden.get_orden_abierta_by_rfid(db=db, tarjeta_id=tarjeta_cliente)
        if orden_in_db is None:
            return None, False, 'No se pudo recuperar una orden abierta para esa tarjeta'
        
        ## Busco un pedido abierto para esa orden
        pedido_in_db = self.get_pedido_abierto_por_orden(db=db, orden_id=orden_in_db.id)
        if pedido_in_db is None:
            return None, False, 'No se encontró un pedido abierto de donde quitar el producto'
        print(f'pedido abierto recuperado id: {pedido_in_db.id}')
        
        ## Busco el renglon a remover
        id_renglon_encontrado = None
        
        renglones_de_orden = crud.renglon.get_by_pedido(
            db=db,
            pedido_id=pedido_in_db.id
        )
        
        for renglon in renglones_de_orden:
            if renglon.producto_id == producto_id:
                id_renglon_encontrado = renglon.id
                break

        if id_renglon_encontrado is None:
            producto_in_db = crud.producto.get(db=db, id=producto_id)
            nombre_producto = producto_in_db.titulo if producto_in_db else None
            return None, False, f'No se encontró un renglon con el producto id {producto_id} - {nombre_producto}'
        
        renglon_removido = crud.renglon.remove(db=db, id=id_renglon_encontrado)
        renglon_removido.producto = crud.producto.get(db=db, id=renglon_removido.producto_id)
        return renglon_removido, True, ''

pedido = CRUDPedido(Pedido)