from typing import Optional, List, TYPE_CHECKING
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from ..inventario_y_promociones.producto import Producto

class RenglonBase(BaseModel):
    cantidad: int
    producto_id: int

class RenglonCreate(RenglonBase):
    pass

class RenglonCreateInternal(RenglonCreate):
    pedido_id: int

class RenglonUpdate(BaseModel):
    pass

class RenglonInDBBase(RenglonBase):
    id: int    
    monto: float
    promocion_aplicada: bool
    pedido_id: int
    
    model_config = ConfigDict(from_attributes=True)

class Renglon(RenglonInDBBase):
    producto: Producto

class RenglonInDB(RenglonInDBBase):
    pass
