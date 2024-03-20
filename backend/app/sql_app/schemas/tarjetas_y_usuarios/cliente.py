from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from .tarjeta import Tarjeta
from .detalles_adicionales import DetallesAdicionales

# Shared properties
class ClienteBase(BaseModel):
    nombre: str

# Properties to receive on item creation
class ClienteCreate(ClienteBase):
    pass

# Properties to receive on item update
class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    contraseña: Optional[str] = None

# Properties shared by models stored in DB
class ClienteInDBBase(ClienteBase):
    id: int
    activa: bool
    model_config = ConfigDict(from_attributes=True)

# Properties to return to client
class Cliente(ClienteInDBBase):
    # tarjeta: Optional[Tarjeta] = None
    # detalles_adicionales: Optional[DetallesAdicionales] = None
    pass

class ClienteWithDetails(Cliente):
    # id_tarjeta: int
    # detalles_adicionales: Optional[DetallesAdicionales] = None
    # cliente: Cliente
    detalle: Optional[DetallesAdicionales] = None
    tarjeta: Optional[Tarjeta] = None
    model_config = ConfigDict(from_attributes=True)

# Properties stored in DB
class ClienteInDB(ClienteInDBBase):
    contraseña: str
