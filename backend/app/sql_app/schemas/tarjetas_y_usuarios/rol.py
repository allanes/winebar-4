from pydantic import BaseModel
from typing import List, Optional

# Shared properties
class RolBase(BaseModel):
    nombre_corto: str
    nombre_largo: str

# Properties to receive on item creation
class RolCreate(RolBase):
    pass

# Properties to receive on item update
class RolUpdate(BaseModel):
    nombre_corto: Optional[str] = None
    nombre_largo: Optional[str] = None

# Properties shared by models stored in DB
class RolInDBBase(RolBase):
    id: int

    class Config:
        orm_mode = True

# Properties to return to client
class Rol(RolInDBBase):
    pass

# Properties properties stored in DB
class RolInDB(RolInDBBase):
    pass
