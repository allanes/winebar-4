from enum import Enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class CategoriasVitte(Enum):
    NO_INFORMA = 1
    INACTIVO = 2
    CLIENTE = 5
    CLIENTE_VIP = 6
    CLIENTE_PREMIUM = 7

# Pydantic Models
class VitteCredencialField(BaseModel):
    id: int = 0
    valor: Optional[str]
    clienteid: int = 0
    tipoId: int = 0

class VitteCategoriaField(BaseModel):
    id: int
    nombre: str
    activo: bool

class VitteEmpresaField(BaseModel):
    id: int
    nombre: str
    activo: bool

class ClienteVitte(BaseModel):
    id: int
    activo: bool
    nombre: str
    apellido: str    
    empresa: Optional[VitteEmpresaField | str]
    empresaId: int    
    telefono: Optional[str] 
    saldo: float
    documento: Optional[str]
    mail: Optional[str] 
    categoria: Optional[VitteCategoriaField]
    categoriaId: int
    credencial: Optional[VitteCredencialField] = None

class VitteCredencialField(BaseModel):
    id: int = 0
    valor: str
    clienteid: int = 0
    tipoId: int = 0

class SaveClienteVitte(ClienteVitte):
    activo: bool = True
    telefono: Optional[str] = None
    documento: Optional[str] = None
    mail: Optional[str] = None
    categoria: Optional[str] = None
    tarjeta: str
    credencial: VitteCredencialField
    montoConsumo: int = 0
    validate_field: str = Field('', alias='validate')

class RespuestaConsumo(BaseModel):
    consumoId: int
    bodega: str
    cliente: str
    variedad: str
    vino: str
    medida: str
    volumen: int
    precio: int
    fecha: datetime