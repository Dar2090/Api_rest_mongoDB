from typing import List
from pydantic import BaseModel

class ResumenMesResponse(BaseModel):
    cantidad_socios_activos: int
    variacion_socios_activos: float
    cantidad_altas: int
    variacion_altas: float
    cantidad_bajas: int
    variacion_bajas: float
    cantidad_inactivaciones_sin_baja: int
    variacion_inactivaciones_sin_baja: float
    
class DatosPorDia(BaseModel):
    fecha: str
    altas: float
    recurrencias: float

class CobrosDiaResponse(BaseModel):
    datos: List[DatosPorDia]
    
class CobrosResumenMesResponse(BaseModel):
    total_cobrado: int
    variación_total_cobrado: float 
    total_cobrado_recurrencias: int
    variacion_total_cobrado_recurrencias: float
    total_cobrado_altas: int
    variacion_total_cobrado_altas: float

class TipoCobro(BaseModel):
    Mensual: float
    Anual: float

class NivelAcceso(BaseModel):
    Local: float
    Plus: float
    Total: float
    
class GraficosResponse(BaseModel):
    porcentaje_cobrado_tipo_cobro: TipoCobro
    porcentaje_cobrado_niveles_acceso: NivelAcceso