from typing import Any, Dict, Optional, List
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from ..base import CRUDBase
from sql_app.models.tarjetas_y_usuarios import ClienteOperaConTarjeta
from sql_app.schemas.tarjetas_y_usuarios.cliente_opera_con_tarjeta import ClienteOperaConTarjetaCreate, ClienteOperaConTarjetaUpdate

class CRUDClienteOperaConTarjeta(CRUDBase[ClienteOperaConTarjeta, ClienteOperaConTarjetaCreate, ClienteOperaConTarjetaUpdate]):
    def get_by_cliente_id(self, db: Session, *, cliente_id: int) -> Optional[ClienteOperaConTarjeta]:
        return db.query(ClienteOperaConTarjeta).filter(ClienteOperaConTarjeta.cliente_id == cliente_id).first()

    def get_by_tarjeta_id(self, db: Session, *, tarjeta_id: int) -> Optional[ClienteOperaConTarjeta]:
        return db.query(ClienteOperaConTarjeta).filter(ClienteOperaConTarjeta.tarjeta_id == tarjeta_id).first()

cliente_opera_con_tarjeta = CRUDClienteOperaConTarjeta(ClienteOperaConTarjeta)
