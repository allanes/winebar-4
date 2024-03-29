from pydantic import BaseModel, ConfigDict, field_serializer
from datetime import datetime
from typing import Optional
from ..serializers import serializer_for_nombre_personal

class TurnoBase(BaseModel):
    abierto_por: int

class TurnoCreate(TurnoBase):
    pass

class TurnoUpdate(BaseModel):
    timestamp_cierre: Optional[datetime] = None
    cerrado_por: Optional[int] = None

class TurnoInDBBase(TurnoBase):
    id: int
    timestamp_apertura: datetime
    cantidad_de_ordenes: int
    cantidad_tapas: int
    cantidad_usuarios_vip: int
    monto_en_caja: float    
    comentarios: Optional[str] = ''
    cerrado_por: Optional[int] = None
    timestamp_cierre: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class Turno(TurnoInDBBase):
    clientes_activos: Optional[int] = 0
    suma_ordenes_cobradas: Optional[float] = 0
    abierto_por_nombre: Optional[str] = ''
    cerrado_por_nombre: Optional[str] = ''

    @field_serializer('abierto_por_nombre')
    def serialize_nombre_abierto(self, abierto_por_nombre: datetime, _info):
        nombre_completo = serializer_for_nombre_personal(self.abierto_por)
        return  nombre_completo
    
    @field_serializer('cerrado_por_nombre')
    def serialize_nombre_cerrado(self, cerrado_por_nombre: datetime, _info):
        nombre_completo = serializer_for_nombre_personal(self.cerrado_por)
        return  nombre_completo

class TurnoInDB(TurnoInDBBase):
    pass

class InfoDeCierre(BaseModel):
    comentarios: str
    monto_en_caja: float