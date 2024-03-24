from typing import Optional, List, TYPE_CHECKING
from pydantic import BaseModel, ConfigDict, field_serializer
from datetime import datetime
from ..validators import custom_pedido_serializer

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
    monto_cargado: Optional[float]

    model_config = ConfigDict(from_attributes=True)

class Pedido(PedidoInDBBase):
    atendido_por_nombre: Optional[str] = ''
    renglones: List['Renglon']

    @field_serializer('atendido_por_nombre')
    def serialize_nombre(self, atendido_por_nombre: datetime, _info):
        nombre_completo = custom_pedido_serializer(self.atendido_por)
        return  nombre_completo

class PedidoInDB(PedidoInDBBase):
    pass

