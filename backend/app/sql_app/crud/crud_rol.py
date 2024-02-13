from .base import CRUDBase
from sql_app.models import Rol
from sql_app.schemas.tarjetas_y_usuarios.rol import RolCreate, RolUpdate

rol = CRUDBase[Rol, RolCreate, RolUpdate](Rol)
