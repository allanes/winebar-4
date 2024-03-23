from datetime import datetime
from sqlalchemy.orm import Session
# from sql_app.crud.base_with_active import CRUDBaseWithActiveField
from sql_app.crud.base import CRUDBase
from sql_app.models.gestion_de_pedidos import OrdenCompra, Configuracion
from sql_app.schemas.gestion_de_pedidos.orden import OrdenCompraAbrir, OrdenCompraUpdate, OrdenCompraCerrar, OrdenCompraCreateInternal, OrdenCompraCerrada
from sql_app.schemas.inventario_y_promociones.producto import ProductoCreate
from sql_app import crud

class CRUDOrden(CRUDBase[OrdenCompra, OrdenCompraAbrir, OrdenCompraUpdate]):
    def get_orden_abierta_by_client(self, db: Session, *, cliente_id: int) -> OrdenCompra | None:
        orden_in_db = db.query(OrdenCompra)
        orden_in_db = orden_in_db.filter(OrdenCompra.cliente_id == cliente_id)
        orden_in_db = orden_in_db.filter(OrdenCompra.cerrada_por is not None)
        orden_in_db = orden_in_db.order_by(OrdenCompra.timestamp_apertura_orden.desc())
        orden_in_db = orden_in_db.first()
        print(f'orden abierta encontrada desde crud_orden: {orden_in_db}. cliente id {cliente_id}')
        return orden_in_db
    
    def get_orden_abierta_by_rfid(self, db: Session, *, tarjeta_id: int) -> OrdenCompra | None:
        cliente_opera_in_db = crud.cliente_opera_con_tarjeta.get_by_tarjeta_id(db=db, tarjeta_id=tarjeta_id)
        if cliente_opera_in_db is None:
            return None
        print(f'cliente recuperado id {cliente_opera_in_db.id_cliente}')
        orden_in_db = self.get_orden_abierta_by_client(db=db, cliente_id=cliente_opera_in_db.id_cliente)        
        return orden_in_db
    
    def abrir_orden(self, db: Session, *, abrir_orden_in: OrdenCompraAbrir) -> OrdenCompra:
        # Recupero pre requisitos (turno actual)
        turno_abierto = crud.turno.get_open_turno(db=db)
        if turno_abierto is None: return None

        # Chequeo si preexiste orden para ese tarjeta:
        orden_preexistente = self.get_orden_abierta_by_rfid(db=db, tarjeta_id=abrir_orden_in.tarjeta_cliente)
        if orden_preexistente is not None:
            print("Ya existe una orden para esa tarjeta")
            return None
        
        cliente_in_db = crud.cliente.get_by_rfid_card(db=db, tarjeta_id=abrir_orden_in.tarjeta_cliente)
        if cliente_in_db is None:
            print("No existe la tarjeta")
            return None
        
        # print(f'tarjeta del cliente: {cliente_in_db.tarjeta}')
        ## Reemplazar
        configuracion = Configuracion()
        configuracion.monto_maximo_orden_def = 200
        configuracion.monto_maximo_pedido_def = 100
        
        orden_in = OrdenCompraCreateInternal(
            precarga_usada=0,
            monto_maximo_orden=configuracion.monto_maximo_orden_def,
            turno_id=turno_abierto.id,
            abierta_por=abrir_orden_in.abierta_por,
            cliente_id=cliente_in_db.id
        )
        
        # Aplico valores pord efecto antes de crear
        orden_in_db = OrdenCompra()
        orden_in_db.timestamp_apertura_orden = datetime.now()
        orden_in_db.monto_cobrado = -1
        orden_in_db.monto_cargado = 0
        orden_in_db.turno_id = turno_abierto.id
        [setattr(orden_in_db, attr, value) for attr, value in orden_in.model_dump().items()]

        # Creo
        orden_in_db = super().create(db=db, obj_in=orden_in_db)
        
        return orden_in_db
    
    def cerrar_orden(self, db: Session, *, orden_in: OrdenCompraCerrar) -> OrdenCompra:
        orden_in_db = self.get_orden_abierta_by_rfid(db=db, tarjeta_id=orden_in.tarjeta_cliente)
        if orden_in_db is None:
            return None
        
        # Check if order is open
        if orden_in_db.cerrada_por is not None:
            return None

        orden_in_db.cerrada_por = orden_in.cerrada_por
        orden_in_db.timestamp_cierre_orden = datetime.now()
        orden_in_db.monto_cobrado = 0
        
        db.commit()
        db.refresh(orden_in_db)
        
        return orden_in_db
    
    def cargar_monto(self, db: Session, *, orden_id: int, monto_a_agregar: float) -> OrdenCompra | None:
        orden_in_db = db.query(OrdenCompra).filter(OrdenCompra.id == orden_id).first()
        if orden_in_db is None:
            return None
        orden_in_db.monto_cargado += monto_a_agregar
        db.commit()
        db.refresh(orden_in_db)
    
        return orden_in_db
    
    def convertir_a_orden_detallada(
        self, db: Session, orden: OrdenCompra
    ) -> OrdenCompraCerrada:
        ## Recupero los pedidos
        pedidos_in_db = crud.pedido.get_pedidos_por_orden(db=db, orden_id=orden.id, asc=False)
        
        ## Recupero detalles del cliente
        detalles_in_db = crud.detalles_adicionales.get_by_cliente_id(
            db=db, cliente_id=orden.cliente.id
        )
        apellido_cliente = ''
        if detalles_in_db is not None:
            if detalles_in_db.apellido is not None:
                apellido_cliente = detalles_in_db.apellido
        nombre_cliente = f'{orden.cliente.nombre} {apellido_cliente}'

        ## Recupero el rol del cliente
        cliente_opera = crud.cliente_opera_con_tarjeta.get_by_cliente_id(
            db=db, cliente_id=orden.cliente.id
        )
        rol = cliente_opera.tarjeta.rol.nombre_corto

        ## Armo el schema de respuesta
        return OrdenCompraCerrada(
            **orden.__dict__,
            pedidos = pedidos_in_db,
            nombre_cliente=nombre_cliente,
            rol = rol,
        )
    
orden = CRUDOrden(OrdenCompra)