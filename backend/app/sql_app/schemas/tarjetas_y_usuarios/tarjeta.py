from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .rol import Rol

# Shared properties
class TarjetaBase(BaseModel):
    pass

# Properties to receive on item creation
class TarjetaCreate(TarjetaBase):
    raw_rfid: str
    rol_nombre: str

# Properties to receive on item update
class TarjetaUpdate(BaseModel):
    fecha_ultimo_uso: Optional[datetime] = None
    entregada: Optional[bool] = None
    presente_en_salon: Optional[bool] = None
    monto_precargado: Optional[float] = None
    rol_nombre: Optional[str] = None

# Properties shared by models stored in DB
class TarjetaInDBBase(TarjetaBase):
    id: int
    raw_rfid: str
    activa: bool
    fecha_alta: Optional[datetime]
    fecha_ultimo_uso: Optional[datetime]
    entregada: bool
    presente_en_salon: bool
    monto_precargado: float
    rol_id: int

    class Config:
        orm_mode = True

# Properties to return to client
class Tarjeta(TarjetaInDBBase):
    rol: Rol

# Properties stored in DB
class TarjetaInDB(TarjetaInDBBase):
    pass
