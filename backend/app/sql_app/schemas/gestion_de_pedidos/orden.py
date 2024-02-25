from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class OrdenCompraBase(BaseModel):
    precarga_usada: float
    monto_maximo_orden: float
    turno_id: int
    cliente_id: int

class OrdenCompraCreate(OrdenCompraBase):
    pass

class OrdenCompraUpdate(BaseModel):
    timestamp_cierre_orden: Optional[datetime] = None
    cerrada_por: Optional[int] = None

class OrdenCompraInDBBase(OrdenCompraBase):
    id: int
    turno_id: int
    monto_cobrado: float
    cliente_id: int
    abierta_por: int
    timestamp_apertura_orden: datetime
    cerrada_por: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

class OrdenCompra(OrdenCompraInDBBase):
    pass

class OrdenCompraInDB(OrdenCompraInDBBase):
    pass
