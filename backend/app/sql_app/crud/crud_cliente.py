from typing import Any, Dict, Optional, List, Union
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from sql_app.crud.base_with_active import CRUDBaseWithActiveField
from sql_app.crud import crud_detalles_adicionales, crud_cliente_opera_con_tarjeta
from sql_app.models.tarjetas_y_usuarios import Cliente
from sql_app.schemas.tarjetas_y_usuarios.cliente import ClienteCreate, ClienteUpdate
from sql_app.schemas.tarjetas_y_usuarios.detalles_adicionales import DetallesAdicionalesForUI, DetallesAdicionalesCreate, DetallesAdicionalesUpdate
from sql_app.schemas.tarjetas_y_usuarios.cliente_opera_con_tarjeta import ClienteOperaConTarjetaCreate

class CRUDCliente(CRUDBaseWithActiveField[Cliente, ClienteCreate, ClienteUpdate]):
    ### Functions override section
    def pre_create_checks(self, obj_in: ClienteCreate, db: Session = None) -> tuple[bool, str]:
        # Check if cliente_in.tarjeta_id is available for use
        # Check if cliente_in.tarjeta_id can be lended to a client
        # Check if cliente_in.tarjeta_id is available for use in vitte
        return super().pre_create_checks(obj_in, db)
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
    ) -> Cliente:
        # Create client
        cliente_in_db = super().create_or_reactivate(db=db, obj_in=cliente_in)

        # Create detalles_adicionales
        if detalles_adicionales_in:
            detalles_adicionales_con_id_cliente = DetallesAdicionalesCreate(
                cliente_id=cliente_in_db.id,
                **detalles_adicionales_in.model_dump())
            
            crud_detalles_adicionales.detalles_adicionales.create(
                db=db, obj_in=detalles_adicionales_con_id_cliente)

        # Create cliente_y_tarjetas asociation
        cliente_con_tarjeta = ClienteOperaConTarjetaCreate(
            cliente_id=cliente_in_db.id,
            tarjeta_id=tarjeta_id)

        crud_cliente_opera_con_tarjeta.cliente_opera_con_tarjeta.create(
            db=db, obj_in=cliente_con_tarjeta)
        
        # Open an order
        # Setup Vitte init

        return cliente_in_db

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

cliente = CRUDCliente(Cliente)
