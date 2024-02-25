from typing import TYPE_CHECKING, Optional
from pydantic import BaseModel, ConfigDict
from .producto import ProductoCreate, Producto

class TapaBase(BaseModel):
    foto: Optional[str] = None

class TapaCreate(TapaBase):
    id_producto: int

class TapaConProductoCreate(TapaBase, ProductoCreate):
    pass

class TapaUpdate(TapaBase):
    pass

class TapaInDBBase(TapaBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class Tapa(TapaInDBBase):
    producto: Optional['Producto']
    # pass

class TapaInDB(TapaInDBBase):
    pass
