from typing import Optional, List, TYPE_CHECKING
from pydantic import BaseModel, ConfigDict
from datetime import datetime

# if TYPE_CHECKING:
#     from ..inventario_y_promociones.producto import Producto

# Shared properties
class LectorTapaBase(BaseModel):
    nombre_puerto: Optional[str] = None
    nombre_terminal: str
    id_producto: Optional[int] = None

class LectorTapaReceive(BaseModel):
    lista_lectores_disponibles: list[str]
    
# Properties to receive on item creation
class LectorTapaCreate(LectorTapaBase):
    pass
    
# Properties to receive on item update
class LectorTapaUpdate(BaseModel):
    id_producto: Optional[int] = None
    nombre_puerto: Optional[str] = None

# Properties shared by models stored in DB
class LectorTapaInDBBase(LectorTapaBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Properties to return to client
class LectorTapa(LectorTapaInDBBase):
    pass

# Properties stored in DB
class LectorTapaInDB(LectorTapaInDBBase):
    pass
