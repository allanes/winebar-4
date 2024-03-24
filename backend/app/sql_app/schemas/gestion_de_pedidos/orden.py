from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from .pedido import Pedido

class OrdenCompraBase(BaseModel):
    precarga_usada: float
    monto_maximo_orden: float
    turno_id: int
    cliente_id: int
    abierta_por: int

class OrdenCompraAbrir(BaseModel):
    abierta_por: int
    tarjeta_cliente: int

class OrdenCompraCerrar(BaseModel):
    cerrada_por: int
    tarjeta_cliente: int

class OrdenCompraCreateInternal(OrdenCompraBase):
    pass

class OrdenCompraUpdate(BaseModel):
    timestamp_cierre_orden: Optional[datetime] = None
    cerrada_por: Optional[int] = None

class OrdenCompraInDBBase(OrdenCompraBase):
    id: int
    turno_id: int
    monto_cargado: float
    monto_cobrado: float
    timestamp_apertura_orden: datetime
    timestamp_cierre_orden: Optional[datetime] = None
    cerrada_por: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

class OrdenCompra(OrdenCompraInDBBase):
    pass

class OrdenCompraCerrada(OrdenCompra):
    pedidos: list[Pedido]
    nombre_cliente: str
    rol: str

class OrdenCompraInDB(OrdenCompraInDBBase):
    pass
