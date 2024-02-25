from typing import List, Optional, TYPE_CHECKING
from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from .producto import Producto

# Shared properties
class MenuBase(BaseModel):
    pass

# Properties to receive on item creation
class MenuCreate(MenuBase):
    pass

# Properties to receive on item update
class MenuUpdate(MenuBase):
    pass

# Properties shared by models stored in DB
class MenuInDBBase(MenuBase):
    id: int
    productos: List['Producto'] = []

    model_config = ConfigDict(from_attributes=True)

# Properties to return to client
class Menu(MenuInDBBase):
    pass

# Properties stored in DB
class MenuInDB(MenuInDBBase):
    pass
