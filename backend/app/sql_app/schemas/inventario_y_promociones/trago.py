from typing import TYPE_CHECKING, Optional
from pydantic import BaseModel, ConfigDict

class TragoBase(BaseModel):
    foto: Optional[str] = None

class TragoCreate(TragoBase):
    pass

class TragoUpdate(TragoBase):
    pass

class TragoInDBBase(TragoBase):
    id: int
    id_producto: int
    model_config = ConfigDict(from_attributes=True)

class Trago(TragoInDBBase):
    pass

class TragoInDB(TragoInDBBase):
    pass
