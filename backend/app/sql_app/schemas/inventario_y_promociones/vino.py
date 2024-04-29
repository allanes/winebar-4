from typing import TYPE_CHECKING, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class VinoBase(BaseModel):
    id_vitte: Optional[int] = None
    volumen: int

class VinoCreate(VinoBase):
    id_producto: int

class VinoUpdate(VinoBase):
    pass

class VinoInDBBase(VinoBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class Vino(VinoInDBBase):
    pass

class VinoInDB(VinoInDBBase):
    pass
