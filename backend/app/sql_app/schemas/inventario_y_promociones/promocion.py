from typing import List, Optional, TYPE_CHECKING
from pydantic import BaseModel, ConfigDict
from datetime import datetime

if TYPE_CHECKING:
    from .producto_promocion import ProductoPromocion

class PromocionBase(BaseModel):
    descuento: float
    vigencia_desde: datetime
    vigencia_hasta: datetime

class PromocionCreate(PromocionBase):
    pass

class PromocionUpdate(PromocionBase):
    pass

class PromocionInDBBase(PromocionBase):
    id: int
    productos: List['ProductoPromocion'] = []
    model_config = ConfigDict(from_attributes=True)

class Promocion(PromocionInDBBase):
    pass

class PromocionInDB(PromocionInDBBase):
    pass
