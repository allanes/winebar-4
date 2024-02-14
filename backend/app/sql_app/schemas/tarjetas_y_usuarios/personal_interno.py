from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .tarjeta import Tarjeta

# Shared properties
class PersonalInternoBase(BaseModel):
    id: int
    tarjeta_id: Optional[int]
    nombre: str
    apellido: str
    telefono: Optional[str]

# Properties to receive on item creation
class PersonalInternoCreate(PersonalInternoBase):
    contra_sin_hash: Optional[str]
        
# Properties to receive on item update
class PersonalInternoUpdate(BaseModel):
    nombre: Optional[str]
    apellido: Optional[str]
    contra_sin_hash: Optional[str]

# Properties shared by models stored in DB
class PersonalInternoInDBBase(PersonalInternoBase):
    usuario: str
    activo: bool
    
    # tarjeta: Tarjeta
    class Config:
        orm_mode = True

# Properties to return to client
class PersonalInterno(PersonalInternoInDBBase):
    pass

# Properties stored in DB
class PersonalInternoInDB(PersonalInternoInDBBase):
    contraseña: str
