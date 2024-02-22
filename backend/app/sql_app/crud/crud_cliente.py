from typing import Any, Dict, Optional, List
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from .base_with_active import CRUDBaseWithActiveField
from ..models.tarjetas_y_usuarios import Cliente
from ..schemas.tarjetas_y_usuarios.cliente import ClienteCreate, ClienteUpdate

class CRUDCliente(CRUDBaseWithActiveField[Cliente, ClienteCreate, ClienteUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Cliente]:
        return db.query(Cliente).filter(Cliente.nombre == name).first()

    def create_with_tarjeta(self, db: Session, *, obj_in: ClienteCreate, tarjeta_id: int) -> Cliente:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db_obj.tarjeta_id = tarjeta_id
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

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
