from pydantic import ConfigDict, BaseModel
from typing import List, Optional
from datetime import datetime

# Shared properties
class ConfiguracionBase(BaseModel):
    monto_maximo_orden_def: Optional[float]
    monto_maximo_pedido_def: Optional[float]

# Properties to receive on item creation
class ConfiguracionCreate(ConfiguracionBase):
    pass

# Properties to receive on item update
class ConfiguracionUpdate(BaseModel):
    pass

# Properties shared by models stored in DB
class ConfiguracionInDBBase(ConfiguracionBase):
    id: int
    fecha_ultima_actualizacion: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

# Properties to return to client
class Configuracion(ConfiguracionInDBBase):
    pass
# Properties stored in DB
class ConfiguracionInDB(ConfiguracionInDBBase):
    pass
