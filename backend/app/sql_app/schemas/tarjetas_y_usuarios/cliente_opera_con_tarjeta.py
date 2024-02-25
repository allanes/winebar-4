from pydantic import BaseModel
from .tarjeta import Tarjeta
from .cliente import Cliente

class ClienteOperaConTarjetaBase(BaseModel):
    id_cliente: int
    tarjeta_id: int

# Properties to receive on item creation
class ClienteOperaConTarjetaCreate(ClienteOperaConTarjetaBase):
    pass

# Properties to receive on item update
class ClienteOperaConTarjetaUpdate(ClienteOperaConTarjetaBase):
    pass

# Properties shared by models stored in DB
class ClienteOperaConTarjetaInDBBase(ClienteOperaConTarjetaBase):
    id: int
    id_cliente: int | None
    tarjeta_id: int | None

    tarjeta: Tarjeta | None
    cliente: Cliente | None

# Properties to return to client
class ClienteOperaConTarjeta(ClienteOperaConTarjetaInDBBase):
    pass

# Properties stored in DB
class ClienteOperaConTarjetaInDB(ClienteOperaConTarjetaInDBBase):
    pass
