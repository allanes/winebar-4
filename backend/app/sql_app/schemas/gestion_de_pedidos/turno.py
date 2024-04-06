from pydantic import BaseModel, ConfigDict, field_serializer
from datetime import datetime
from typing import Optional
from ..serializers import (
    serializer_for_nombre_personal, 
    serializer_for_suma_ordenes_para_turno,
    serializer_for_clientes_activos,
    serializer_for_clientes_totales
)

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
    abierto_por_nombre: Optional[str] = ''
    cerrado_por_nombre: Optional[str] = ''
    suma_ordenes_cobradas: Optional[float] = 0
    diferencia: Optional[float] = None

    @field_serializer('abierto_por_nombre')
    def serialize_nombre_abierto(self, abierto_por_nombre: str, _info):
        nombre_completo = serializer_for_nombre_personal(self.abierto_por)
        return  nombre_completo
    
    @field_serializer('cerrado_por_nombre')
    def serialize_nombre_cerrado(self, cerrado_por_nombre: str, _info):
        nombre_completo = serializer_for_nombre_personal(self.cerrado_por)
        return  nombre_completo
    
    @field_serializer('suma_ordenes_cobradas')
    def serialize_suma_ordenes_cobradas(self, suma_ordenes_cobradas: float, _info):
        if self.suma_ordenes_cobradas is not None and self.suma_ordenes_cobradas != 0:
            print(f'no se serializará la suma_ordenes_cobradas para turno {self.id}')
            return self.suma_ordenes_cobradas
        
        suma_ordenes = serializer_for_suma_ordenes_para_turno(turno_id=self.id)
        return  suma_ordenes
    
    @field_serializer('diferencia')
    def serialize_diferencia(self, diferencia: str, _info):
        if not self.timestamp_cierre:
            print(f'no se pudo serializar la diferencia para turno {self.id}')
            return None

        suma_ordenes = serializer_for_suma_ordenes_para_turno(turno_id=self.id)        
        dif = self.monto_en_caja - suma_ordenes
        return  dif
    
    @field_serializer('clientes_activos')
    def serialize_clientes_activos(self, clientes_activos: int, _info):
        if self.timestamp_cierre:
            return 0
        
        cant_clientes_activos = serializer_for_clientes_activos(
            turno_id=self.id
        )
        return  cant_clientes_activos
    
    @field_serializer('cantidad_de_ordenes')
    def serialize_clientes_totales(self, cantidad_de_ordenes: int, _info):
        cant_clientes_totales = serializer_for_clientes_totales(
            turno_id=self.id
        )
        return  cant_clientes_totales

class TurnoInDB(TurnoInDBBase):
    pass

class InfoDeCierre(BaseModel):
    comentarios: str
    monto_en_caja: float