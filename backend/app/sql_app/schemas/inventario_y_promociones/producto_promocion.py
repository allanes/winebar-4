from typing import TYPE_CHECKING
from pydantic import BaseModel, ConfigDict

class ProductoPromocionBase(BaseModel):
    id_producto: int
    id_promocion: int

class ProductoPromocionCreate(ProductoPromocionBase):
    pass

class ProductoPromocionUpdate(ProductoPromocionBase):
    pass

class ProductoPromocionInDBBase(ProductoPromocionBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class ProductoPromocion(ProductoPromocionInDBBase):
    pass

class ProductoPromocionInDB(ProductoPromocionInDBBase):
    pass
