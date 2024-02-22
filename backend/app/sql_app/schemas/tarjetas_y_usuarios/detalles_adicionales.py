from pydantic import BaseModel
from typing import Optional

class DetallesAdicionalesBase(BaseModel):
    dni: Optional[int] = None
    apellido: Optional[str] = None
    email: Optional[str] = None
    teléfono: Optional[str] = None
    domicilio: Optional[str] = None

# Properties to receive on item creation
class DetallesAdicionalesCreate(DetallesAdicionalesBase):
    pass

# Properties to receive on item update
class DetallesAdicionalesUpdate(DetallesAdicionalesBase):
    pass

# Properties shared by models stored in DB
class DetallesAdicionalesInDBBase(DetallesAdicionalesBase):
    id: int
    cliente_id: int

# Properties to return to client
class DetallesAdicionales(DetallesAdicionalesInDBBase):
    pass

# Properties stored in DB
class DetallesAdicionalesInDB(DetallesAdicionalesInDBBase):
    pass
