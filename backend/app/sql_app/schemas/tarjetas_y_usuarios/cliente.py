from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from .tarjeta import Tarjeta

# Shared properties
class ClienteBase(BaseModel):
    nombre: str

# Properties to receive on item creation
class ClienteCreate(ClienteBase):
    contraseña: str

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
    pass

# Properties stored in DB
class ClienteInDB(ClienteInDBBase):
    contraseña: str
