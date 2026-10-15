from threading import Lock
from typing import Any, Dict, Optional, List, Union
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from sql_app.crud.base_with_active import CRUDBaseWithActiveField
from sql_app.crud.tarjetas_y_usuarios import crud_detalles_adicionales, crud_cliente_opera_con_tarjeta, crud_tarjeta, crud_rol
from sql_app.crud.gestion_de_pedidos import crud_orden, crud_configuracion
from sql_app.models.tarjetas_y_usuarios import Cliente, ClienteOperaConTarjeta, Tarjeta
from sql_app.models.gestion_de_pedidos import OrdenCompra, Pedido, Renglon
from sql_app.schemas.tarjetas_y_usuarios.cliente import ClienteCreate, ClienteUpdate
from sql_app.schemas.tarjetas_y_usuarios.detalles_adicionales import DetallesAdicionales, DetallesAdicionalesForUI, DetallesAdicionalesCreate, DetallesAdicionalesUpdate
from sql_app.schemas.tarjetas_y_usuarios.cliente_opera_con_tarjeta import ClienteOperaConTarjetaCreate
from sql_app.schemas.gestion_de_pedidos.orden import OrdenCompraAbrir
from sql_app.schemas.gestion_de_pedidos.configuracion import ConfiguracionCreate
from sql_app.core.security import hashear_contra, crear_nombre_usuario, obtener_pass_de_deactivacion, generar_pass_por_defecto
from sql_app.api.vitte_integration.vitte_utils import vitte_api_client
from sql_app.api.vitte_integration.vitte_service import vitte_service
from sql_app.schemas.validators import get_now_time

_lock_liberar_pendientes = Lock()

class CRUDCliente(CRUDBaseWithActiveField[Cliente, ClienteCreate, ClienteUpdate]):
    ### Functions override section
    def apply_activation_defaults(self, obj_in: ClienteCreate | ClienteUpdate, db_obj: Cliente, db: Session = None) -> Cliente:
        print('aplicando activation defaults')
        cliente_in_db = db_obj
        cliente_in = obj_in
        default_pass = generar_pass_por_defecto(cliente_in=cliente_in)

        cliente_in_db.activa = True
        cliente_in_db.nombre = cliente_in.nombre
        cliente_in_db.contraseña = hashear_contra(contra_in=default_pass)        

        return cliente_in_db
    
    def apply_deactivation_defaults(self, db_obj: Cliente, db: Session = None) -> None:
        db_obj.activa = False
        cliente_opera = crud_cliente_opera_con_tarjeta.cliente_opera_con_tarjeta.get_by_cliente_id(
            db=db, cliente_id=db_obj.id
        )
        if cliente_opera is not None:
            crud_cliente_opera_con_tarjeta.cliente_opera_con_tarjeta.remove(
                db=db, id=cliente_opera.id
            )

        return db_obj
    
    ### End of Functions override section
    
    def get_by_name(self, db: Session, *, name: str) -> Optional[Cliente]:
        return db.query(Cliente).filter(Cliente.nombre == name).first()

    def create_with_tarjeta(
        self, 
        db: Session, 
        *, 
        cliente_in: ClienteCreate, 
        tarjeta_id: int, 
        usuario_apertura_orden: int,
        detalles_adicionales_in: DetallesAdicionalesForUI = None,
        montos_config_in: ConfiguracionCreate | None
    ) -> tuple[Cliente | None, bool, str]:
        # Tarjeta prechecks
        puede_asociarse, msg = self.pre_entrega_checks(db=db, tarjeta_id=tarjeta_id)
        if not puede_asociarse:
            return None, False, msg

        try:
            vitte_service.require_online(vitte_api_client.check_health)
        except RuntimeError as err:
            return None, False, f'No se puede crear el cliente: Vitte no esta disponible. {err}'
        
        cliente_in_db = self.create(db=db, obj_in=cliente_in)

        # Create detalles_adicionales
        if detalles_adicionales_in:
            detalles_adicionales_con_id_cliente = DetallesAdicionalesCreate(
                cliente_id=cliente_in_db.id,
                **detalles_adicionales_in.model_dump())
            
            detalles_in_db = crud_detalles_adicionales.detalles_adicionales.create(
                db=db, obj_in=detalles_adicionales_con_id_cliente)
            
        cliente_operando, pudo_entregar, msg = self.entregar_tarjeta_a_cliente(db=db, cliente_id=cliente_in_db.id, tarjeta_id=tarjeta_id)
        
        if not pudo_entregar:
            ## Remove Cliente and Additional Details
            return None, False, msg

        db.refresh(cliente_in_db)
        
        # Open an order
        orden_in = OrdenCompraAbrir(
            abierta_por=usuario_apertura_orden,
            tarjeta_cliente=tarjeta_id
        )
        orden_abierta_in_db = crud_orden.orden.abrir_orden(db=db, abrir_orden_in=orden_in, montos_config=montos_config_in)
        
        # Setup Vitte init
        msg = ''
        vitte_api_client.cargar_o_actualizar_cliente_vitte(
            cliente_id = cliente_in_db.id,
            cliente_nombre = cliente_in_db.nombre,
            raw_tarjeta_id = cliente_operando.tarjeta.raw_rfid
        )
        saldo_cargado = vitte_api_client.cargar_saldo_cliente(
            tarjeta_rfid = cliente_operando.tarjeta.raw_rfid,
            monto_a_agregar = orden_abierta_in_db.monto_maximo_orden,
        )
        if not saldo_cargado:
            return None, False, 'No se pudo cargar saldo en Vitte.'
        
        return cliente_in_db, True, msg

    def update_with_tarjeta(self, db: Session, *, db_obj: Cliente, obj_in: Union[ClienteUpdate, Dict[str, Any]], tarjeta_id: Optional[int] = None) -> Cliente:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        if tarjeta_id is not None:
            db_obj.tarjeta_id = tarjeta_id
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_rfid_card(self, db: Session, *, tarjeta_id: int) -> Cliente:
        cliente_con_tarjeta_in_db = crud_cliente_opera_con_tarjeta.cliente_opera_con_tarjeta.get_by_tarjeta_id(db=db, tarjeta_id=tarjeta_id)
        if cliente_con_tarjeta_in_db is None: return None

        cliente_in_db = db.query(Cliente).filter(
            Cliente.id == cliente_con_tarjeta_in_db.id_cliente
        ).first()

        return cliente_in_db
    
    def get_multi_with_tarjeta(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Cliente]:
        cliente_opera_con_tarjeta_records = db.query(ClienteOperaConTarjeta).offset(skip).limit(limit).all()

        # Extract all cliente IDs from the ClienteOperaConTarjeta records
        cliente_ids = [record.id_cliente for record in cliente_opera_con_tarjeta_records]

        # Query to get all clients that are present in the ClienteOperaConTarjeta table
        clientes_con_tarjeta = db.query(Cliente).filter(Cliente.id.in_(cliente_ids)).all()

        return clientes_con_tarjeta
    
    def pre_entrega_checks(self, db: Session, tarjeta_id: int) -> tuple[bool, str]:
        """Chequeos para entregar/cambiar tarjeta.
        """
        tarjeta_puede_usarse, msg_puede_usarse = crud_tarjeta.tarjeta.check_tarjeta_libre_para_asociar_cliente(db=db, id_tarjeta=tarjeta_id)
        if not tarjeta_puede_usarse:
            return False, msg_puede_usarse
        
        ## chequeo que noe exista orden abierta para esa tarjeta
        orden_preexistente = crud_orden.orden.get_orden_abierta_by_rfid(db=db, tarjeta_id=tarjeta_id)
        if orden_preexistente is not None:
            return False, "Ya existe una orden abierta para esa tarjeta."

        # If all checks pass, the tarjeta can be associated
        return True, ''
    
    def entregar_tarjeta_a_cliente(
        self, db: Session, cliente_id: int, tarjeta_id: int
    ) -> tuple[ClienteOperaConTarjeta | None, bool, str]:

        # Create cliente_y_tarjetas asociation
        cliente_con_tarjeta = ClienteOperaConTarjetaCreate(
            id_cliente=cliente_id,
            tarjeta_id=tarjeta_id)

        cliente_operando_in_db = crud_cliente_opera_con_tarjeta.cliente_opera_con_tarjeta.create(
            db=db, obj_in=cliente_con_tarjeta)
        
        tarjeta = db.query(Tarjeta).filter(Tarjeta.id == tarjeta_id).first()
        if tarjeta:
            ts_ultimo_uso = get_now_time()
            tarjeta.entregada = True
            tarjeta.presente_en_salon = True
            tarjeta.fecha_ultimo_uso = ts_ultimo_uso
            tarjeta.monto_precargado = 0
            # Commit the transaction to save changes
            db.commit()
            # Refresh the instances to reflect the updated state
            db.refresh(tarjeta)

            cliente_in_db = db.query(Cliente)
            cliente_in_db = cliente_in_db.filter(Cliente.id == cliente_id)
            cliente_in_db = cliente_in_db.first()

            nombre_rol = crud_rol.rol.get(db=db, id=tarjeta.rol_id)
            nombre_rol = nombre_rol.nombre_corto if nombre_rol else None
            cliente_in_db.rol_usado_nombre = nombre_rol
            db.commit()
            db.refresh(cliente_in_db)
        
        return cliente_operando_in_db, True, ''
    
    def devolver_tarjeta_de_cliente(
        self, db: Session, id: int
    ) -> tuple[Tarjeta | None, bool, str]:
        cliente_opera = crud_cliente_opera_con_tarjeta.cliente_opera_con_tarjeta.get_by_cliente_id(
            db=db, cliente_id=id
        )
        if cliente_opera is None:
            return None, False, f'No se encontró un cliente operando con el cliente_id {id}'
        
        cliente = self.get_active(db=db, id=id)
        tarjeta = crud_tarjeta.tarjeta.get_active(db=db, id=cliente_opera.tarjeta_id)
        
        print(f'BORRANDO CLIENTE EN VITTE')
        vitte_service.require_online(vitte_api_client.check_health)
        pudo_inhabilitar = vitte_api_client.inhabilitar_cliente_vitte(
            # data_cliente=cliente_opera,
            cliente_id=id,
            cliente_nombre=cliente.nombre,
            raw_tarjeta_rfid=tarjeta.raw_rfid
        )
        if not pudo_inhabilitar:
            raise RuntimeError('No se pudo inhabilitar el cliente en Vitte.')
        
        tarjeta_devuelta = crud_tarjeta.tarjeta.devolver_a_banca(db=db, id=cliente_opera.tarjeta_id)
        return tarjeta_devuelta

    def liberar_tarjetas_pendientes(self, db: Session) -> int:
        """Libera las tarjetas de ordenes ya cerradas cuya baja en Vitte no pudo completarse.

        Pasa cuando se pierde la conexion con Vitte despues de cerrar la orden. Se llama
        al recuperar la conexion y devuelve la cantidad de tarjetas liberadas.
        """
        if not _lock_liberar_pendientes.acquire(blocking=False):
            return 0

        liberadas = 0
        try:
            asociaciones = db.query(ClienteOperaConTarjeta)
            asociaciones = asociaciones.join(Tarjeta, Tarjeta.id == ClienteOperaConTarjeta.tarjeta_id)
            asociaciones = asociaciones.filter(Tarjeta.presente_en_salon == True)
            asociaciones = asociaciones.order_by(ClienteOperaConTarjeta.id.desc())
            asociaciones = asociaciones.all()

            tarjetas_vistas = set()
            for asociacion in asociaciones:
                # Solo cuenta el ultimo cliente que recibio cada tarjeta
                if asociacion.tarjeta_id in tarjetas_vistas:
                    continue
                tarjetas_vistas.add(asociacion.tarjeta_id)

                ultima_orden = crud_orden.orden.get_by_cliente_id(db=db, cliente_id=asociacion.id_cliente)
                if ultima_orden is None:
                    continue
                orden_abierta = crud_orden.orden.get_orden_abierta_by_client(db=db, cliente_id=asociacion.id_cliente)
                if orden_abierta is not None:
                    continue

                tarjeta = asociacion.tarjeta
                cliente = self.get(db=db, id=asociacion.id_cliente)
                cliente_en_vitte = vitte_api_client.buscar_cliente_vitte_por_tarjeta_raw(tarjeta_id=tarjeta.raw_rfid)
                if ultima_orden.cerrada_sin_vitte:
                    # Antes de dar de baja al cliente, dejo asentado lo que no se llego a cobrar
                    self._anotar_consumos_sin_cobrar(db=db, orden=ultima_orden)
                if cliente_en_vitte is not None:
                    pudo_inhabilitar = vitte_api_client.inhabilitar_cliente_vitte(
                        cliente_id=asociacion.id_cliente,
                        cliente_nombre=cliente.nombre if cliente else '',
                        raw_tarjeta_rfid=tarjeta.raw_rfid
                    )
                    if not pudo_inhabilitar:
                        continue

                crud_tarjeta.tarjeta.devolver_a_banca(db=db, id=tarjeta.id)
                liberadas += 1
                print(f'Tarjeta {tarjeta.id} liberada (estaba pendiente desde el cierre de la orden {ultima_orden.id})')

                turno = ultima_orden.turno
                if turno is not None and turno.cerrado_por is not None:
                    crud_cliente_opera_con_tarjeta.cliente_opera_con_tarjeta.remove(db=db, id=asociacion.id)
        except Exception as err:
            print(f'No se pudieron liberar las tarjetas pendientes: {err}')
        finally:
            _lock_liberar_pendientes.release()

        return liberadas

    def _anotar_consumos_sin_cobrar(self, db: Session, orden) -> None:
        """Para una orden cerrada sin conexion, anota en sus comentarios los consumos de vino
        que Vitte tiene registrados y que no entraron en el cobro."""
        marca = 'Consumos de vino sin cobrar'
        if orden.comentarios and marca in orden.comentarios:
            return
        consumos = vitte_api_client.consultar_transacciones_vino_por_cliente(
            cliente_id=orden.cliente_id,
            fecha_alta_cliente=orden.timestamp_apertura_orden
        )
        registrados = db.query(Renglon.vitte_consumo_id).join(Pedido, Pedido.id == Renglon.pedido_id)
        registrados = registrados.filter(Pedido.orden_id == orden.id)
        registrados = {fila[0] for fila in registrados.all() if fila[0] is not None}
        faltantes = [consumo for consumo in consumos if consumo.consumoId not in registrados]
        total = sum(consumo.precio for consumo in faltantes)
        nota = f'{marca}: {len(faltantes)} por ${total:.2f}.'
        orden.comentarios = f'{orden.comentarios or ""} {nota}'.strip()
        db.commit()

    def aplicar_descuentos_pendientes(self, db: Session) -> int:
        """Descuenta del saldo en Vitte las tapas confirmadas mientras no habia conexion."""
        aplicados = 0
        try:
            ordenes = db.query(OrdenCompra)
            ordenes = ordenes.filter(OrdenCompra.cerrada_por.is_(None))
            ordenes = ordenes.filter(OrdenCompra.descuento_vitte_pendiente > 0)
            for orden in ordenes.all():
                asociacion = crud_cliente_opera_con_tarjeta.cliente_opera_con_tarjeta.get_by_cliente_id(
                    db=db, cliente_id=orden.cliente_id
                )
                if asociacion is None or asociacion.tarjeta is None:
                    continue
                descontado = vitte_api_client.cargar_saldo_cliente(
                    tarjeta_rfid=asociacion.tarjeta.raw_rfid,
                    monto_a_agregar=-(orden.descuento_vitte_pendiente)
                )
                if descontado:
                    orden.descuento_vitte_pendiente = 0
                    db.commit()
                    aplicados += 1
        except Exception as err:
            print(f'No se pudieron aplicar los descuentos pendientes en Vitte: {err}')
        return aplicados

cliente = CRUDCliente(Cliente)
