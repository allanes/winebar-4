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
    timestamp_pedido: Optional[datetime]
    cerrado: bool
    orden_id: int
    monto_maximo_pedido: float    

    model_config = ConfigDict(from_attributes=True)

class Pedido(PedidoInDBBase):
    renglones: List['Renglon']

class PedidoInDB(PedidoInDBBase):
    pass
