from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .tarjeta import Tarjeta
from sql_app import schemas

# Shared properties
class PersonalInternoBase(BaseModel):
    id: int
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
    activa: bool
    
    # tarjeta: Tarjeta
    class Config:
        orm_mode = True

# Properties to return to client
class PersonalInterno(PersonalInternoInDBBase):
    tarjeta: Optional[schemas.Tarjeta] = None

# Properties stored in DB
class PersonalInternoInDB(PersonalInternoInDBBase):
    contraseña: str
    tarjeta_id: Optional[int]

class PersonalInternoYTarjeta(BaseModel):
    personal_id: int
    tarjeta_id: int

