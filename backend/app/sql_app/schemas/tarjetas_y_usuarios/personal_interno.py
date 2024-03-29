from pydantic import ConfigDict, BaseModel
from typing import List, Optional
from datetime import datetime
from .tarjeta import Tarjeta
from sql_app import schemas

# Shared properties
class PersonalInternoBase(BaseModel):
    id: int
    nombre: str
    apellido: str
    telefono: Optional[str] = None

# Properties to receive on item creation
class PersonalInternoCreate(PersonalInternoBase):
    pass
        
# Properties to receive on item update
class PersonalInternoUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None

# Properties shared by models stored in DB
class PersonalInternoInDBBase(PersonalInternoBase):
    usuario: str
    activa: bool
    model_config = ConfigDict(from_attributes=True)

# Properties to return to client
class PersonalInterno(PersonalInternoInDBBase):
    tarjeta: Optional[schemas.Tarjeta] = None

# Properties stored in DB
class PersonalInternoInDB(PersonalInternoInDBBase):
    contraseña: str
    tarjeta_id: Optional[int] = None

class PersonalInternoYTarjeta(BaseModel):
    personal_id: int
    tarjeta_id: int

