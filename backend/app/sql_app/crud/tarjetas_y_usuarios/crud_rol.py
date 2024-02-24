from typing import Optional
from sqlalchemy.orm import Session
from sql_app.crud.base import CRUDBase
from sql_app.models import Rol
from sql_app.schemas.tarjetas_y_usuarios.rol import RolCreate, RolUpdate

class CRUDRol(CRUDBase[Rol, RolCreate, RolUpdate]):
    def get_by_name(seld, db: Session, name: str) -> Optional[Rol]:
        return db.query(Rol).filter(Rol.nombre_corto == name).first()

rol = CRUDRol(Rol)
