from typing import Any, Dict, Optional, List
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from .base import CRUDBase
from ..models.tarjetas_y_usuarios import DetallesAdicionales
from ..schemas.tarjetas_y_usuarios.detalles_adicionales import DetallesAdicionalesCreate, DetallesAdicionalesUpdate

class CRUDDetallesAdicionales(CRUDBase[DetallesAdicionales, DetallesAdicionalesCreate, DetallesAdicionalesUpdate]):
    def get_by_cliente_id(self, db: Session, *, cliente_id: int) -> Optional[DetallesAdicionales]:
        return db.query(DetallesAdicionales).filter(DetallesAdicionales.cliente_id == cliente_id).first()

detalles_adicionales = CRUDDetallesAdicionales(DetallesAdicionales)
