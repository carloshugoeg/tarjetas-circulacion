from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from backend.models.models import (
    EstadoTarjetaEnum, TipoCombustibleEnum, UsoVehiculoEnum, 
    TipoCambioEnum, TipoAlertaEnum, EstadoAlertaEnum
)

# --- BASE SCHEMAS ---

class DepartamentoBase(BaseModel):
    nombre: str
    codigo: str

class Departamento(DepartamentoBase):
    id_departamento: int
    model_config = ConfigDict(from_attributes=True)

class MunicipioBase(BaseModel):
    id_departamento: int
    nombre: str

class Municipio(MunicipioBase):
    id_municipio: int
    model_config = ConfigDict(from_attributes=True)

class TipoVehiculoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class TipoVehiculo(TipoVehiculoBase):
    id_tipo_vehiculo: int
    model_config = ConfigDict(from_attributes=True)

class MarcaVehiculoBase(BaseModel):
    nombre: str

class MarcaVehiculo(MarcaVehiculoBase):
    id_marca: int
    model_config = ConfigDict(from_attributes=True)

class LineaVehiculoBase(BaseModel):
    id_marca: int
    nombre: str

class LineaVehiculo(LineaVehiculoBase):
    id_linea: int
    model_config = ConfigDict(from_attributes=True)

class ColorBase(BaseModel):
    nombre: str

class Color(ColorBase):
    id_color: int
    model_config = ConfigDict(from_attributes=True)

# --- ACTORS SCHEMAS ---

class UsuarioSistemaBase(BaseModel):
    username: str
    nombre_completo: str
    activo: bool = True

class UsuarioSistemaCreate(UsuarioSistemaBase):
    pass

class UsuarioSistema(UsuarioSistemaBase):
    id_usuario: int
    fecha_creacion: datetime
    model_config = ConfigDict(from_attributes=True)

class PropietarioBase(BaseModel):
    dpi: str = Field(..., pattern=r'^\d{13}$')
    primer_nombre: str
    segundo_nombre: Optional[str] = None
    primer_apellido: str
    segundo_apellido: Optional[str] = None
    fecha_nacimiento: date
    direccion: str
    id_municipio: int
    telefono: Optional[str] = Field(None, pattern=r'^\d{8}$')
    correo: Optional[str] = None
    nit: Optional[str] = None

class PropietarioCreate(PropietarioBase):
    pass

class PropietarioUpdate(BaseModel):
    dpi: Optional[str] = Field(None, pattern=r'^\d{13}$')
    primer_nombre: Optional[str] = None
    segundo_nombre: Optional[str] = None
    primer_apellido: Optional[str] = None
    segundo_apellido: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    direccion: Optional[str] = None
    id_municipio: Optional[int] = None
    telefono: Optional[str] = Field(None, pattern=r'^\d{8}$')
    correo: Optional[str] = None
    nit: Optional[str] = None

class Propietario(PropietarioBase):
    id_propietario: int
    fecha_registro: datetime
    model_config = ConfigDict(from_attributes=True)

# --- VEHICULO SCHEMAS ---

class VehiculoBase(BaseModel):
    vin: str = Field(..., pattern=r'^[A-HJ-NPR-Z0-9]{17}$')
    placa: str = Field(..., pattern=r'^[A-Z]{1,2}-?\d{2,4}[A-Z]{2,3}$')
    id_tipo_vehiculo: int
    id_marca: int
    id_linea: int
    modelo_anio: int
    id_color: int
    numero_motor: str
    numero_chasis: str
    cilindros: Optional[int] = None
    cilindrada_cc: Optional[int] = None
    ejes: int = 2
    tonelaje: Optional[Decimal] = None
    pasajeros: Optional[int] = None
    combustible: TipoCombustibleEnum
    uso: UsoVehiculoEnum = UsoVehiculoEnum.PARTICULAR

    @field_validator("modelo_anio")
    @classmethod
    def validate_modelo_anio(cls, value: int):
        max_year = date.today().year + 1
        if value < 1900 or value > max_year:
            raise ValueError(f"modelo_anio debe estar entre 1900 y {max_year}")
        return value

class VehiculoCreate(VehiculoBase):
    pass

class VehiculoUpdate(BaseModel):
    vin: Optional[str] = Field(None, pattern=r'^[A-HJ-NPR-Z0-9]{17}$')
    placa: Optional[str] = Field(None, pattern=r'^[A-Z]{1,2}-?\d{2,4}[A-Z]{2,3}$')
    id_tipo_vehiculo: Optional[int] = None
    id_marca: Optional[int] = None
    id_linea: Optional[int] = None
    modelo_anio: Optional[int] = None
    id_color: Optional[int] = None
    numero_motor: Optional[str] = None
    numero_chasis: Optional[str] = None
    cilindros: Optional[int] = None
    cilindrada_cc: Optional[int] = None
    ejes: Optional[int] = None
    tonelaje: Optional[Decimal] = None
    pasajeros: Optional[int] = None
    combustible: Optional[TipoCombustibleEnum] = None
    uso: Optional[UsoVehiculoEnum] = None

    @field_validator("modelo_anio")
    @classmethod
    def validate_modelo_anio(cls, value: Optional[int]):
        if value is None:
            return value
        max_year = date.today().year + 1
        if value < 1900 or value > max_year:
            raise ValueError(f"modelo_anio debe estar entre 1900 y {max_year}")
        return value

class Vehiculo(VehiculoBase):
    id_vehiculo: int
    fecha_registro: datetime
    model_config = ConfigDict(from_attributes=True)

# --- TARJETA CIRCULACION SCHEMAS ---

class TarjetaCirculacionBase(BaseModel):
    id_vehiculo: int
    id_propietario: int
    numero_tarjeta: str
    fecha_emision: date
    fecha_vencimiento: date
    estado: EstadoTarjetaEnum = EstadoTarjetaEnum.VIGENTE
    id_usuario_emision: Optional[int] = None
    observaciones: Optional[str] = None

    @model_validator(mode="after")
    def validate_fecha_vencimiento(self):
        if self.fecha_vencimiento <= self.fecha_emision:
            raise ValueError("fecha_vencimiento debe ser posterior a fecha_emision")
        return self

class TarjetaCirculacionCreate(TarjetaCirculacionBase):
    pass

class TarjetaCirculacionUpdate(BaseModel):
    id_vehiculo: Optional[int] = None
    id_propietario: Optional[int] = None
    numero_tarjeta: Optional[str] = None
    fecha_emision: Optional[date] = None
    fecha_vencimiento: Optional[date] = None
    estado: Optional[EstadoTarjetaEnum] = None
    id_usuario_emision: Optional[int] = None
    observaciones: Optional[str] = None

    @model_validator(mode="after")
    def validate_fecha_vencimiento(self):
        if (
            self.fecha_emision is not None
            and self.fecha_vencimiento is not None
            and self.fecha_vencimiento <= self.fecha_emision
        ):
            raise ValueError("fecha_vencimiento debe ser posterior a fecha_emision")
        return self


class CambioPropietarioRequest(BaseModel):
    nuevo_propietario_id: int
    usuario_id: Optional[int] = None


class CambioMotorRequest(BaseModel):
    nuevo_motor: str = Field(..., min_length=1)
    usuario_id: Optional[int] = None


class CambioColorRequest(BaseModel):
    nuevo_color_id: int
    usuario_id: Optional[int] = None


class DesactivarTarjetaRequest(BaseModel):
    nuevo_estado: EstadoTarjetaEnum
    motivo: Optional[str] = None
    usuario_id: Optional[int] = None


class ReactivarTarjetaRequest(BaseModel):
    motivo: Optional[str] = None
    usuario_id: Optional[int] = None

class TarjetaCirculacion(TarjetaCirculacionBase):
    id_tarjeta: int
    fecha_registro: datetime
    model_config = ConfigDict(from_attributes=True)

# --- HISTORIAL CAMBIOS SCHEMAS ---

class HistorialCambiosBase(BaseModel):
    id_tarjeta: int
    tipo_cambio: TipoCambioEnum
    valor_anterior: Optional[str] = None
    valor_nuevo: str
    usuario_responsable: Optional[int] = None

class HistorialCambios(HistorialCambiosBase):
    id_historial: int
    fecha_hora: datetime
    model_config = ConfigDict(from_attributes=True)

# --- ALERTA SCHEMAS ---

class AlertaBase(BaseModel):
    id_tarjeta: int
    tipo_alerta: TipoAlertaEnum
    estado_alerta: EstadoAlertaEnum = EstadoAlertaEnum.ACTIVA
    dias_umbral: Optional[int] = None
    atendida_por: Optional[int] = None
    fecha_atencion: Optional[datetime] = None
    descripcion: Optional[str] = None

class Alerta(AlertaBase):
    id_alerta: int
    fecha_generacion: datetime
    model_config = ConfigDict(from_attributes=True)
