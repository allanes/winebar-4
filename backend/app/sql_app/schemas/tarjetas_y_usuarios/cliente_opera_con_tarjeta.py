from pydantic import BaseModel

class ClienteOperaConTarjetaBase(BaseModel):
    cliente_id: int
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

# Properties to return to client
class ClienteOperaConTarjeta(ClienteOperaConTarjetaInDBBase):
    pass

# Properties stored in DB
class ClienteOperaConTarjetaInDB(ClienteOperaConTarjetaInDBBase):
    pass
