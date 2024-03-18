from typing import TYPE_CHECKING, Optional
from pydantic import BaseModel, ConfigDict
from .producto import ProductoCreate, ProductoUpdate, Producto

class TapaBase(BaseModel):
    foto: Optional[str] = None

class TapaCreate(TapaBase):
    id_producto: int

class TapaConProductoCreate(ProductoCreate):
    foto: Optional[str] = None

class TapaUpdate(ProductoUpdate):
    foto: Optional[str] = None


class TapaInDBBase(TapaBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class Tapa(TapaInDBBase):
    producto: Optional['Producto']
    # pass

class TapaInDB(TapaInDBBase):
    pass
