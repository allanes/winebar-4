from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class TurnoBase(BaseModel):
    abierto_por: int

class TurnoCreate(TurnoBase):
    pass

class TurnoUpdate(BaseModel):
    timestamp_cierre: Optional[datetime] = None
    cerrado_por: Optional[int] = None

class TurnoInDBBase(TurnoBase):
    id: int
    timestamp_apertura: datetime
    cantidad_de_ordenes: int
    cantidad_tapas: int
    cantidad_usuarios_vip: int
    ingresos_totales: float    
    cerrado_por: Optional[int] = None
    timestamp_cierre: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class Turno(TurnoInDBBase):
    clientes_activos: Optional[int] = 0

class TurnoInDB(TurnoInDBBase):
    pass
