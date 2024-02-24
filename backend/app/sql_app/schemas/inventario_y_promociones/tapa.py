from typing import TYPE_CHECKING, Optional
from pydantic import BaseModel, ConfigDict

class TapaBase(BaseModel):
    foto: Optional[str] = None

class TapaCreate(TapaBase):
    pass

class TapaUpdate(TapaBase):
    pass

class TapaInDBBase(TapaBase):
    id: int
    id_producto: int
    model_config = ConfigDict(from_attributes=True)

class Tapa(TapaInDBBase):
    pass

class TapaInDB(TapaInDBBase):
    pass
