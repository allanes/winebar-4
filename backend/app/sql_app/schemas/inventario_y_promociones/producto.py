from typing import Optional, List, TYPE_CHECKING
from pydantic import BaseModel, ConfigDict, PydanticUndefinedAnnotation
from datetime import datetime

if TYPE_CHECKING:
    from .tapa import Tapa
    from .trago import Trago
    from .vino import Vino

# Shared properties
class ProductoBase(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[float] = None
    stock: Optional[int] = None

    class Config:
        extra = "allow"

# Properties to receive on item creation
class ProductoCreate(ProductoBase):
    titulo: str
    precio: float
    
# Properties to receive on item update
class ProductoUpdate(ProductoBase):
    pass

# Properties shared by models stored in DB
class ProductoInDBBase(ProductoBase):
    id: int
    activa: bool
    ultimo_cambio_precio: datetime
    id_menu: Optional[int] = None

    # tapa: Optional['Tapa'] = None
    # trago: Optional['Trago'] = None
    # vino: Optional['Vino'] = None
    
    model_config = ConfigDict(from_attributes=True)

# Properties to return to client
class Producto(ProductoInDBBase):
    pass

# Properties stored in DB
class ProductoInDB(ProductoInDBBase):
    pass
