from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Shared properties
class TarjetaBase(BaseModel):
    raw_rfid: str
    activa: Optional[bool] = True
    fecha_alta: Optional[datetime] = None
    fecha_ultimo_uso: Optional[datetime] = None
    entregada: Optional[bool] = None
    presente_en_salon: Optional[bool] = None
    monto_precargado: Optional[float] = None
    rol_id: int

# Properties to receive on item creation
class TarjetaCreate(TarjetaBase):
    pass

# Properties to receive on item update
class TarjetaUpdate(BaseModel):
    raw_rfid: Optional[str] = None
    activa: Optional[bool] = None
    entregada: Optional[bool] = None
    presente_en_salon: Optional[bool] = None
    monto_precargado: Optional[float] = None
    rol_id: Optional[int] = None

# Properties shared by models stored in DB
class TarjetaInDBBase(TarjetaBase):
    id: int
    fecha_alta: datetime

    class Config:
        orm_mode = True

# Properties to return to client
class Tarjeta(TarjetaInDBBase):
    pass

# Properties stored in DB
class TarjetaInDB(TarjetaInDBBase):
    pass
