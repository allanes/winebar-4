from typing import Any, Dict, Optional, List, Union
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from sql_app.crud.base_with_active import CRUDBaseWithActiveField
from sql_app.crud.tarjetas_y_usuarios import crud_detalles_adicionales, crud_cliente_opera_con_tarjeta, crud_tarjeta
from sql_app.models.tarjetas_y_usuarios import Cliente, ClienteOperaConTarjeta
from sql_app.schemas.tarjetas_y_usuarios.cliente import ClienteCreate, ClienteUpdate
from sql_app.schemas.tarjetas_y_usuarios.detalles_adicionales import DetallesAdicionales, DetallesAdicionalesForUI, DetallesAdicionalesCreate, DetallesAdicionalesUpdate
from sql_app.schemas.tarjetas_y_usuarios.cliente_opera_con_tarjeta import ClienteOperaConTarjetaCreate
from sql_app.core.security import hashear_contra, crear_nombre_usuario, obtener_pass_de_deactivacion, generar_pass_por_defecto

class CRUDCliente(CRUDBaseWithActiveField[Cliente, ClienteCreate, ClienteUpdate]):
    ### Functions override section
    def pre_create_checks(self, obj_in: ClienteCreate, db: Session = None) -> tuple[bool, str]:
        # Check if cliente_in.tarjeta_id is available for use
        # Check if cliente_in.tarjeta_id can be lended to a client
        # Check if cliente_in.tarjeta_id is available for use in vitte
        return super().pre_create_checks(obj_in, db)
    
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
        detalles_adicionales_in: DetallesAdicionalesForUI = None
    ) -> tuple[Cliente | None, bool, str]:
        # Tarjeta prechecks
        puede_asociarse, msg = crud_tarjeta.tarjeta.check_tarjeta_libre_para_asociar_cliente(db=db, id_tarjeta=tarjeta_id)
        if not puede_asociarse:
            return None, False, msg
        
        # Client prechecks
        check_passed, message = self.pre_create_checks(
            db=db,
            obj_in=cliente_in
        )
        if not check_passed:
            return None, False, message
        
        cliente_in_db = self.create(db=db, obj_in=cliente_in)
        
        # Create detalles_adicionales
        if detalles_adicionales_in:
            detalles_adicionales_con_id_cliente = DetallesAdicionalesCreate(
                cliente_id=cliente_in_db.id,
                **detalles_adicionales_in.model_dump())
            
            detalles_in_db = crud_detalles_adicionales.detalles_adicionales.create(
                db=db, obj_in=detalles_adicionales_con_id_cliente)
            
        # Create cliente_y_tarjetas asociation
        cliente_con_tarjeta = ClienteOperaConTarjetaCreate(
            id_cliente=cliente_in_db.id,
            tarjeta_id=tarjeta_id)

        crud_cliente_opera_con_tarjeta.cliente_opera_con_tarjeta.create(
            db=db, obj_in=cliente_con_tarjeta)
        
        db.refresh(cliente_in_db)
        
        # Open an order
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

cliente = CRUDCliente(Cliente)
