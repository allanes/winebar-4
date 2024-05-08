from enum import Enum
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field

class CategoriasVitte(Enum):
    CLIENTE = 1
    CLIENTE_VIP = 2
    CLIENTE_PREMIUM = 3

# Pydantic Models
class VitteCredencialField(BaseModel):
    id: int = 0
    valor: Optional[str] = ''
    clienteId: int = 0
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
    activo: bool = True
    nombre: str
    apellido: str    
    empresa: Optional[VitteEmpresaField | str]
    empresaId: int    
    telefono: Optional[str] = None
    saldo: float
    montoConsumo: float
    documento: Optional[str] = None
    mail: Optional[str] = None
    categoria: Optional[VitteCategoriaField] = None
    categoriaId: int
    credencial: Optional[VitteCredencialField] = None

class ClienteVitteDesdeMaquina(BaseModel):
    nombre: Optional[str]
    apellido: Optional[str] = None
    empresa: Optional[VitteEmpresaField] = None
    empresaId: int
    telefono: Optional[str] = None
    saldo: float
    documento: Optional[str] = None
    mail: Optional[str] = None
    categoria: Optional[VitteCategoriaField] = None
    categoriaId: int
    credenciales: Optional[VitteCredencialField] = None
    id: int
    activo: bool


class VitteCredencialField(BaseModel):
    id: int = 0
    valor: str
    clienteid: int = 0
    tipoId: int = 0

class SaveClienteVitte(ClienteVitte):
    tarjeta: str
    id: int = 0
    montoConsumo: float = 0.0
    
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

class TransaccionVino(BaseModel):
    consumoId: int
    bodega: str
    cliente: str
    variedad: str
    vino: str
    medida: str
    volumen: float
    precio: float
    fecha: datetime

class VinoVariedad(BaseModel):
    nombre: Optional[str] = None
    id: Optional[int] = None
    activo: Optional[bool] = None

class VinoBodega(BaseModel):
    nombre: Optional[str] = None
    id: Optional[int] = None
    activo: Optional[bool] = None

class VinoInVitte(BaseModel):
    nombre: Optional[str] = None
    empresa: Optional[Any] = None
    empresaId: Optional[int] = None
    variedad: Optional[VinoVariedad] = None
    variedadId: Optional[int] = None
    bodega: Optional[VinoBodega] = None
    bodegaId: Optional[int] = None
    origen: Optional[Any] = None
    origenId: Optional[int] = None
    notas: Optional[str] = None
    foto: Optional[str] = None
    volumen: Optional[float] = None
    precios: Optional[Any] = None
    id: Optional[int] = None
    activo: Optional[bool] = None
    
class PicoDeModulo(BaseModel):
    id: Optional[int] = None
    orden: Optional[int] = None
    vinoId: Optional[int] = None
    vino: Optional[VinoInVitte] = None
    colocacion: Optional[int] = None
    limpieza: Optional[int] = None
    degustacionMl: Optional[int] = None
    degustacionPrecio: Optional[float] = None
    mediaMl: Optional[int] = None
    mediaPrecio: Optional[float] = None
    copaMl: Optional[int] = None
    copaPrecio: Optional[float] = None
    volumen: Optional[float] = None
    muestraImagen: Optional[bool] = None
    recambioAutomatico: Optional[bool] = None
    logoMaquinaPath: Optional[str] = None