from typing import Optional, List, TYPE_CHECKING
from pydantic import BaseModel, ConfigDict
from datetime import datetime

# if TYPE_CHECKING:
from .renglon import Renglon

class PedidoBase(BaseModel):
    atendido_por: int

class PedidoCreate(PedidoBase):
    pass

class PedidoUpdate(BaseModel):
    pass

class PedidoInDBBase(PedidoBase):
    id: int
    timestamp_pedido: datetime
    cerrado: bool
    promocion_aplicada: bool
    orden_id: int    

    model_config = ConfigDict(from_attributes=True)

class Pedido(PedidoInDBBase):
    renglon: List['Renglon']

class PedidoInDB(PedidoInDBBase):
    pass
