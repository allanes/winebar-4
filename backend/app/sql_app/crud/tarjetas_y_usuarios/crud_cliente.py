from typing import Any, Dict, Optional, List, Union
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from sql_app.crud.base_with_active import CRUDBaseWithActiveField
from sql_app.crud.tarjetas_y_usuarios import crud_detalles_adicionales, crud_cliente_opera_con_tarjeta, crud_tarjeta
from sql_app.crud.gestion_de_pedidos import crud_orden
from sql_app.models.tarjetas_y_usuarios import Cliente, ClienteOperaConTarjeta, Tarjeta
from sql_app.schemas.tarjetas_y_usuarios.cliente import ClienteCreate, ClienteUpdate
from sql_app.schemas.tarjetas_y_usuarios.detalles_adicionales import DetallesAdicionales, DetallesAdicionalesForUI, DetallesAdicionalesCreate, DetallesAdicionalesUpdate
from sql_app.schemas.tarjetas_y_usuarios.cliente_opera_con_tarjeta import ClienteOperaConTarjetaCreate
from sql_app.schemas.gestion_de_pedidos.orden import OrdenCompraAbrir
from sql_app.core.security import hashear_contra, crear_nombre_usuario, obtener_pass_de_deactivacion, generar_pass_por_defecto

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
        detalles_adicionales_in: DetallesAdicionalesForUI = None
    ) -> tuple[Cliente | None, bool, str]:
        # Tarjeta prechecks
        puede_asociarse, msg = self.pre_entrega_checks(db=db, tarjeta_id=tarjeta_id)
        if not puede_asociarse:
            return None, False, msg
        
        cliente_in_db = self.create(db=db, obj_in=cliente_in)

        # Create detalles_adicionales
        if detalles_adicionales_in:
            detalles_adicionales_con_id_cliente = DetallesAdicionalesCreate(
                cliente_id=cliente_in_db.id,
                **detalles_adicionales_in.model_dump())
            
            detalles_in_db = crud_detalles_adicionales.detalles_adicionales.create(
                db=db, obj_in=detalles_adicionales_con_id_cliente)
            
        _, pudo_entregar, msg = self.entregar_tarjeta_a_cliente(db=db, cliente_id=cliente_in_db.id, tarjeta_id=tarjeta_id)
        
        if not pudo_entregar:
            ## Remove Cliente and Additional Details
            return None, False, msg

        db.refresh(cliente_in_db)
        
        # Open an order
        orden_in = OrdenCompraAbrir(
            abierta_por=usuario_apertura_orden,
            tarjeta_cliente=tarjeta_id
        )
        crud_orden.orden.abrir_orden(db=db, abrir_orden_in=orden_in)
        # Setup Vitte init
        
        return cliente_in_db, True, ''

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
            tarjeta.entregada = True
            tarjeta.presente_en_salon = True
            tarjeta.fecha_ultimo_uso = datetime.now()
            tarjeta.monto_precargado = 0
            # Commit the transaction to save changes
            db.commit()
            # Refresh the instances to reflect the updated state
            db.refresh(tarjeta)
        
        return cliente_operando_in_db, True, ''
    
    def devolver_tarjeta_de_cliente(
        self, db: Session, id: int
    ) -> tuple[Tarjeta | None, bool, str]:
        cliente_opera = crud_cliente_opera_con_tarjeta.cliente_opera_con_tarjeta.get_by_cliente_id(
            db=db, cliente_id=id
        )
        if cliente_opera is None:
            return None, False, f'No se encontró un cliente operando con el cliente_id {id}'
        
        tarjeta_devuelta = crud_tarjeta.tarjeta.devolver_a_banca(db=db, id=cliente_opera.tarjeta_id)
        return tarjeta_devuelta        

cliente = CRUDCliente(Cliente)
