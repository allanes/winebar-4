from typing import TYPE_CHECKING, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class VinoBase(BaseModel):
    id_vitte: Optional[int] = None

class VinoCreate(VinoBase):
    pass

class VinoUpdate(VinoBase):
    pass

class VinoInDBBase(VinoBase):
    id: int
    id_producto: int
    model_config = ConfigDict(from_attributes=True)

class Vino(VinoInDBBase):
    pass

class VinoInDB(VinoInDBBase):
    pass
