from typing import List
from sqlalchemy.orm import Session
# from sql_app.crud.base_with_active import CRUDBaseWithActiveField
from sql_app.crud.base import CRUDBase
from sql_app.models.gestion_de_pedidos import OrdenCompra, Renglon
from sql_app.schemas.gestion_de_pedidos.orden import OrdenCompraAbrir, OrdenCompraUpdate, OrdenCompraInfoPago, OrdenCompraCreateInternal, OrdenCompraDetallada
from sql_app.schemas.gestion_de_pedidos.configuracion import ConfiguracionCreate
from sql_app import crud
# from sql_app.api.vitte_integration.vitte_utils import vitte_api_client
from sql_app.api.fudo_integration import fudo_crud
from sql_app.api.vitte_integration.vitte_service import vitte_service
from sql_app.api.fudo_integration.fudo_schemas import FudoExportItem, FudoItemType, FudoExportRequest
from sql_app.schemas.validators import get_now_time

class CRUDOrden(CRUDBase[OrdenCompra, OrdenCompraAbrir, OrdenCompraUpdate]):
    def get_by_cliente_id(self, db: Session, *, cliente_id: int) -> OrdenCompra | None:
        orden = db.query(OrdenCompra)
        orden = orden.filter(OrdenCompra.cliente_id == cliente_id)
        orden = orden.first()
        return orden
    
    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[OrdenCompra]:
        ordenes = db.query(OrdenCompra)
        ordenes = ordenes.order_by(OrdenCompra.timestamp_cierre_orden.desc())
        ordenes = ordenes.offset(skip)
        ordenes = ordenes.limit(limit)
        ordenes = ordenes.all()

        return ordenes
    
    def get_by_turno_id(
        self, db: Session, turno_id: int
    ) -> List[OrdenCompra]:
        if not turno_id: 
            return None
        
        ordenes = db.query(OrdenCompra)
        ordenes = ordenes.filter(OrdenCompra.turno_id == turno_id)
        ordenes = ordenes.order_by(OrdenCompra.timestamp_cierre_orden.desc())
        ordenes = ordenes.all()
        return ordenes
    
    def get_orden_abierta_by_client(self, db: Session, *, cliente_id: int) -> OrdenCompra | None:
        orden_in_db = db.query(OrdenCompra)
        orden_in_db = orden_in_db.filter(OrdenCompra.cliente_id == cliente_id)
        orden_in_db = orden_in_db.filter(OrdenCompra.cerrada_por.is_(None))
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
    
    def get_ordenes_abiertas_by_name(self, db: Session, *, client_name: str) -> OrdenCompra | None:
        clientes_operando = crud.cliente_opera_con_tarjeta.get_multi_by_client_name(
            db=db, client_name=client_name
        )
        cliente_ids = [cliente_operando.id_cliente for cliente_operando in clientes_operando]
        print(f'clientes operando recuperados: {cliente_ids}')

        ordenes_in_db = db.query(OrdenCompra)
        ordenes_in_db = ordenes_in_db.filter(OrdenCompra.cerrada_por.is_(None)) # Solo las abiertas
        ordenes_in_db = ordenes_in_db.filter(OrdenCompra.cliente_id.in_(cliente_ids))
        ordenes_in_db = ordenes_in_db.order_by(OrdenCompra.timestamp_apertura_orden.desc())
        ordenes_in_db = ordenes_in_db.all()
        
        return ordenes_in_db
    
    def abrir_orden(
        self, 
        db: Session, 
        *, 
        abrir_orden_in: OrdenCompraAbrir, 
        montos_config: ConfiguracionCreate | None = None
    ) -> OrdenCompra:
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
        
        # Seteo montos maximos
        ultima_config_in_db = crud.configuracion.get_last(db=db)
        configuracion_montos = ConfiguracionCreate(
            monto_maximo_orden_def=ultima_config_in_db.monto_maximo_orden_def,
            monto_maximo_pedido_def=ultima_config_in_db.monto_maximo_pedido_def            
        )
        
        if montos_config is not None:
            if montos_config.monto_maximo_pedido_def:
                configuracion_montos.monto_maximo_pedido_def = montos_config.monto_maximo_pedido_def
            if montos_config.monto_maximo_orden_def:
                configuracion_montos.monto_maximo_orden_def = montos_config.monto_maximo_orden_def
        
        orden_in = OrdenCompraCreateInternal(
            precarga_usada=0,
            monto_maximo_orden=configuracion_montos.monto_maximo_orden_def,
            monto_maximo_pedido=configuracion_montos.monto_maximo_pedido_def,
            turno_id=turno_abierto.id,
            abierta_por=abrir_orden_in.abierta_por,
            cliente_id=cliente_in_db.id
        )
        
        # Aplico valores pord efecto antes de crear
        ts_apertura = get_now_time()
        orden_in_db = OrdenCompra()
        orden_in_db.timestamp_apertura_orden = ts_apertura
        orden_in_db.monto_cargado = 0
        orden_in_db.monto_cobrado = 0
        orden_in_db.monto_cobrado_efectivo = 0
        orden_in_db.monto_cobrado_tarjeta = 0
        orden_in_db.monto_cobrado_transferencia = 0
        orden_in_db.monto_cargado_fudo = 0
        orden_in_db.turno_id = turno_abierto.id
        [setattr(orden_in_db, attr, value) for attr, value in orden_in.model_dump().items()]

        # Creo
        orden_in_db = super().create(db=db, obj_in=orden_in_db)
        
        return orden_in_db
    
    def cerrar_orden(self, db: Session, *, id: int, cerrada_por_id: int, info_pago: OrdenCompraInfoPago) -> tuple[OrdenCompra | None, bool, str]:
        orden_in_db = db.query(OrdenCompra)
        orden_in_db = orden_in_db.filter(OrdenCompra.id == id)
        orden_in_db = orden_in_db.first()
        
        if orden_in_db is None:
            return None, False, f'No se encontró la orden id {id}'
        
        # Check if order is open
        if orden_in_db.cerrada_por is not None:
            personal = crud.personal_interno.get(db=db, id=orden_in_db.cerrada_por)
            return None, False, f'La orden id {id} ya está cerrada por {personal.nombre}'
        
        # Remove any opened Pedido for that order
        pedido_abierto = crud.pedido.get_pedido_abierto_por_orden(db=db, orden_id=orden_in_db.id)
        if pedido_abierto is not None:
            pedido_removido = crud.pedido.remove(db=db, id=pedido_abierto.id)
            print(f'Removiendo pedido. Pedido removido: {pedido_removido.__dict__ if pedido_removido else ""}')
            
        # Calculo valores necesarios
        ts_cierre = get_now_time()
        print(f'Cerrando orden con timestamp {ts_cierre.isoformat()}')
        
        cobrado_efectivo = info_pago.cobrado_efectivo if info_pago.cobrado_efectivo else 0
        cobrado_tarjeta = info_pago.cobrado_tarjeta if info_pago.cobrado_tarjeta else 0
        cobrado_transferencia = info_pago.cobrado_transferencia if info_pago.cobrado_transferencia else 0
        cargado_en_fudo = orden_in_db.monto_cargado if info_pago.carga_fudo_venta_id else 0
        
        ## Verifico que el monto cobrado sea igual al monto cargado
        suma_pagos = cobrado_efectivo + cobrado_tarjeta + cobrado_transferencia + cargado_en_fudo

        if suma_pagos != orden_in_db.monto_cargado:
            msg = f'La suma cobrada (${suma_pagos}) debe ser igual que la suma cargada (${orden_in_db.monto_cargado})'
            return None, False, msg
        
        # Reviso si debo exportar a fudo
        exportar_a_fudo = info_pago.carga_fudo_venta_id
        if exportar_a_fudo:
            export_result, msg = self._exportar_orden_a_fudo(db=db, orden=orden_in_db, info_pago=info_pago)

            if not export_result:
                return orden_in_db, False, msg

            numero_venta = info_pago.carga_fudo_venta_id
            numero_mesa = fudo_crud.get_table_number_by_sale_id(sale_id=numero_venta)
            info_pago.comentarios = f'Orden imputada en venta {numero_venta} (mesa {numero_mesa}) de FUDO. {info_pago.comentarios}'

        orden_in_db.cerrada_por = cerrada_por_id
        orden_in_db.timestamp_cierre_orden = ts_cierre
        orden_in_db.monto_cobrado_efectivo = cobrado_efectivo
        orden_in_db.monto_cobrado_tarjeta = cobrado_tarjeta
        orden_in_db.monto_cobrado_transferencia = cobrado_transferencia
        orden_in_db.monto_cargado_fudo = cargado_en_fudo
        orden_in_db.monto_cobrado = suma_pagos
        orden_in_db.comentarios = info_pago.comentarios
        if info_pago.cerrar_sin_vitte:
            orden_in_db.cerrada_sin_vitte = True
            orden_in_db.comentarios = f'Cerrada sin conexion con Vitte. {info_pago.comentarios or ""}'.strip()

        db.commit()
        db.refresh(orden_in_db)

        # Devuelvo tarjeta a banca. Si Vitte falla, o si la orden se cerro sin conexion, la orden
        # ya quedo cerrada y la tarjeta se libera mas tarde desde crud.cliente.liberar_tarjetas_pendientes
        if not info_pago.cerrar_sin_vitte:
            try:
                tarjeta_devuelta = crud.cliente.devolver_tarjeta_de_cliente(
                    db=db, id=orden_in_db.cliente_id
                )
            except Exception as err:
                print(f'Orden {orden_in_db.id} cerrada, pero la tarjeta quedo pendiente de liberar: {err}')

        return orden_in_db, True, ''
    
    def sumar_descuento_vitte_pendiente(self, db: Session, *, orden_id: int, monto: float) -> None:
        """Anota un monto de tapas que todavia no pudo descontarse del saldo del cliente en Vitte."""
        orden_in_db = db.query(OrdenCompra).filter(OrdenCompra.id == orden_id).first()
        if orden_in_db is None:
            return
        orden_in_db.descuento_vitte_pendiente = (orden_in_db.descuento_vitte_pendiente or 0) + (monto or 0)
        db.commit()

    def cargar_monto(self, db: Session, *, orden_id: int, monto_a_agregar: float) -> OrdenCompra | None:
        orden_in_db = db.query(OrdenCompra).filter(OrdenCompra.id == orden_id).first()
        if orden_in_db is None:
            return None
        orden_in_db.monto_cargado += monto_a_agregar
        db.commit()
        db.refresh(orden_in_db)
    
        return orden_in_db
    
    def check_orden_no_supera_monto_maximo(
        self, 
        db: Session, 
        orden_id: OrdenCompra
    ) -> tuple[bool, str]:
        orden_obj = self.get(db=db, id=orden_id)
        if not orden_obj:
            return False, 'No se encontró la orden'
        
        suma_orden = 0

        pedidos_de_orden = crud.pedido.get_pedidos_por_orden(db=db, orden_id=orden_obj.id)
        for pedido in pedidos_de_orden:
            renglones_del_pedido = crud.renglon.get_by_pedido(db=db, pedido_id=pedido.id)
            montos_de_renglones = [renglon.monto for renglon in renglones_del_pedido]
            suma_pedido = sum(montos_de_renglones)
            suma_orden += suma_pedido
        
        if suma_orden <= orden_obj.monto_maximo_orden:
            return True, ''
        print(f'suma de la orden al chequear: {suma_orden}')

        return False, f'Supera monto máximo de órden ({orden_obj.monto_maximo_orden})'
    
    def convertir_a_orden_detallada(
        self, db: Session, orden: OrdenCompra
    ) -> OrdenCompraDetallada:
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
        rol = None
        cliente_opera = crud.cliente_opera_con_tarjeta.get_by_cliente_id(
            db=db, cliente_id=orden.cliente.id
        )
        if cliente_opera is not None: # El cliente es historico. busco el rol guardado al cerrar el turno
            rol = cliente_opera.tarjeta.rol.nombre_corto
        else:
            rol = orden.cliente.rol_usado_nombre

        ## Recupero nombre de vendedor
        nombre_vendedor = ''
        if orden.cerrada_por is not None:
            vendedor = crud.personal_interno.get_active(db=db, id=orden.cerrada_por)
            if vendedor is not None:
                nombre_vendedor = f'{vendedor.nombre} {vendedor.apellido}'

        ## Recupero las transacciones de vino desde Vitte
        # transacciones_vino = vitte_api_client.consultar_transacciones_vino_por_cliente(
        #     cliente_id=orden.cliente_id,
        #     fecha_alta_cliente=orden.timestamp_apertura_orden
        # )

        ## Ultima vez que se pudieron traer los consumos de vino de esta tarjeta
        vitte_ultima_sincronizacion = None
        if cliente_opera is not None:
            vitte_ultima_sincronizacion = vitte_service.get_last_consumption_sync(cliente_opera.tarjeta_id)

        ## Armo el schema de respuesta
        return OrdenCompraDetallada(
            **orden.__dict__,
            pedidos = pedidos_in_db,
            nombre_cliente=nombre_cliente,
            rol = rol,
            cerrada_por_nombre=nombre_vendedor,
            vitte_ultima_sincronizacion=vitte_ultima_sincronizacion,
            # consumos_vino=transacciones_vino
        )
    
    def _exportar_orden_a_fudo(self, db: Session, orden: OrdenCompra, info_pago: OrdenCompraInfoPago) -> tuple[bool, str]:
        """Exporta a Fudo un item por cada producto de la orden.

        Cada renglon exportado guarda la venta de Fudo a la que fue, de modo que
        un reintento despues de una falla parcial solo envia lo que falta.
        """
        venta_id = str(info_pago.carga_fudo_venta_id)
        pedidos_de_orden_in_db = crud.pedido.get_pedidos_por_orden(db=db, orden_id=orden.id)
        renglones: List[Renglon] = []
        for pedido in pedidos_de_orden_in_db:
            renglones.extend(crud.renglon.get_by_pedido(db=db, pedido_id=pedido.id))

        ventas_previas = {renglon.fudo_venta_id for renglon in renglones if renglon.fudo_venta_id}
        if ventas_previas and ventas_previas != {venta_id}:
            venta_previa = sorted(ventas_previas)[0]
            return False, f'Parte de esta orden ya fue exportada a la venta {venta_previa} de Fudo. Reintentar sobre esa misma venta.'

        renglones_pendientes = [renglon for renglon in renglones if not renglon.fudo_venta_id]
        items_por_producto = self._prepare_fudo_export_items(
            db=db, orden=orden, info_pago=info_pago, renglones=renglones_pendientes
        )
        for producto_id, item in items_por_producto.items():
            if not fudo_crud.export_item_to_fudo(item):
                return False, "No se pudo exportar a Fudo. Reintentar."

            for renglon in renglones_pendientes:
                if renglon.producto_id == producto_id:
                    renglon.fudo_venta_id = venta_id
            db.commit()

        return True, ''

    def _prepare_fudo_export_items(
        self, db: Session, orden: OrdenCompra, info_pago: OrdenCompraInfoPago, renglones: List[Renglon]
    ) -> dict[int, FudoExportItem]:
        # Grouping by product ID
        grouped_items = {}
        for renglon in renglones:
            if renglon.producto_id not in grouped_items:
                comentario = ""
                tipo = None
                titulo = ""

                # Determine title
                producto_in_db = crud.producto.get_active(db=db, id=renglon.producto_id)
                if producto_in_db:
                    titulo = producto_in_db.titulo

                
                # Determine type (TAPA or VINO)
                tapa = crud.tapa.get_by_product_id(db=db, producto_id=renglon.producto_id)
                if tapa:
                    tipo = FudoItemType.TAPA
                else:
                    vino = crud.vino.get_by_product_id(db=db, producto_id=renglon.producto_id)
                    if vino:
                        tipo = FudoItemType.VINO

                # Create notes/commentaries to add
                comentarios_adicionales = ''
                hay_comentarios_para_agregar = info_pago.comentarios and info_pago.comentarios != ""
                if hay_comentarios_para_agregar:
                    comentarios_adicionales = f'Notas: {info_pago.comentarios}. '

                comentario = f"{titulo} - {comentarios_adicionales}(Orden {orden.id})"

                # Assemble product to export
                grouped_items[renglon.producto_id] = {
                    "quantity": 0,
                    "amount": 0.0,
                    "type": tipo,
                    "comment": comentario
                }
            
            grouped_items[renglon.producto_id]["quantity"] += renglon.cantidad
            grouped_items[renglon.producto_id]["amount"] += renglon.monto

        # Create FudoExportItem for each grouped product ID
        fudo_export_items = {}
        for producto_id, details in grouped_items.items():
            fudo_export_items[producto_id] = FudoExportItem(
                order_id=orden.id,
                type=details["type"],
                amount=details["amount"],
                quantity=details["quantity"],
                comment=details["comment"],
                sale_id=str(info_pago.carga_fudo_venta_id)
            )

        return fudo_export_items
    
orden = CRUDOrden(OrdenCompra)