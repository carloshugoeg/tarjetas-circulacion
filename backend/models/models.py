import enum
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, DateTime, Numeric, Text, BigInteger, Enum as SQLEnum, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.core.database import Base

# --- ENUMS ---

class TipoCambioEnum(str, enum.Enum):
    PROPIETARIO = 'PROPIETARIO'
    MOTOR = 'MOTOR'
    COLOR = 'COLOR'
    ESTADO = 'ESTADO'
    PLACA = 'PLACA'

class TipoAlertaEnum(str, enum.Enum):
    VENCIMIENTO_PROXIMO = 'VENCIMIENTO_PROXIMO'
    IMPAGO = 'IMPAGO'
    SUSPENSION_ADMINISTRATIVA = 'SUSPENSION_ADMINISTRATIVA'

class EstadoAlertaEnum(str, enum.Enum):
    ACTIVA = 'ACTIVA'
    ATENDIDA = 'ATENDIDA'
    RESUELTA = 'RESUELTA'

class EstadoTarjetaEnum(str, enum.Enum):
    VIGENTE = 'VIGENTE'
    VENCIDA = 'VENCIDA'
    SUSPENDIDA = 'SUSPENDIDA'
    CANCELADA = 'CANCELADA'

class TipoCombustibleEnum(str, enum.Enum):
    GASOLINA = 'GASOLINA'
    DIESEL = 'DIESEL'
    ELECTRICO = 'ELECTRICO'
    HIBRIDO = 'HIBRIDO'

class UsoVehiculoEnum(str, enum.Enum):
    PARTICULAR = 'PARTICULAR'
    COMERCIAL = 'COMERCIAL'
    OFICIAL = 'OFICIAL'
    DIPLOMATICO = 'DIPLOMATICO'

# --- MODELS ---

class Departamento(Base):
    __tablename__ = "departamento"
    id_departamento = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False, unique=True)
    codigo = Column(String(2), nullable=False, unique=True)
    
    municipios = relationship("Municipio", back_populates="departamento")

class Municipio(Base):
    __tablename__ = "municipio"
    id_municipio = Column(Integer, primary_key=True, index=True)
    id_departamento = Column(Integer, ForeignKey("departamento.id_departamento"), nullable=False)
    nombre = Column(String(80), nullable=False)
    
    __table_args__ = (UniqueConstraint('id_departamento', 'nombre', name='_id_depto_nombre_uc'),)
    
    departamento = relationship("Departamento", back_populates="municipios")
    propietarios = relationship("Propietario", back_populates="municipio")

class TipoVehiculo(Base):
    __tablename__ = "tipo_vehiculo"
    id_tipo_vehiculo = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False, unique=True)
    descripcion = Column(Text)
    
    vehiculos = relationship("Vehiculo", back_populates="tipo_vehiculo")

class MarcaVehiculo(Base):
    __tablename__ = "marca_vehiculo"
    id_marca = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False, unique=True)
    
    lineas = relationship("LineaVehiculo", back_populates="marca")
    vehiculos = relationship("Vehiculo", back_populates="marca")

class LineaVehiculo(Base):
    __tablename__ = "linea_vehiculo"
    id_linea = Column(Integer, primary_key=True, index=True)
    id_marca = Column(Integer, ForeignKey("marca_vehiculo.id_marca"), nullable=False)
    nombre = Column(String(80), nullable=False)
    
    __table_args__ = (UniqueConstraint('id_marca', 'nombre', name='_id_marca_nombre_uc'),)
    
    marca = relationship("MarcaVehiculo", back_populates="lineas")
    vehiculos = relationship("Vehiculo", back_populates="linea")

class Color(Base):
    __tablename__ = "color"
    id_color = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(30), nullable=False, unique=True)
    
    vehiculos = relationship("Vehiculo", back_populates="color")

class UsuarioSistema(Base):
    __tablename__ = "usuario_sistema"
    id_usuario = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, unique=True)
    nombre_completo = Column(String(150), nullable=False)
    activo = Column(Boolean, nullable=False, default=True)
    fecha_creacion = Column(DateTime, nullable=False, server_default=func.now())
    
    tarjetas_emitidas = relationship("TarjetaCirculacion", back_populates="usuario_emision")
    historial_realizado = relationship("HistorialCambios", back_populates="usuario_responsable_rel")
    alertas_atendidas = relationship("Alerta", back_populates="usuario_atencion")

class Propietario(Base):
    __tablename__ = "propietario"
    id_propietario = Column(Integer, primary_key=True, index=True)
    dpi = Column(String(13), nullable=False, unique=True)
    primer_nombre = Column(String(50), nullable=False)
    segundo_nombre = Column(String(50))
    primer_apellido = Column(String(50), nullable=False)
    segundo_apellido = Column(String(50))
    fecha_nacimiento = Column(Date, nullable=False)
    direccion = Column(String(200), nullable=False)
    id_municipio = Column(Integer, ForeignKey("municipio.id_municipio"), nullable=False)
    telefono = Column(String(15))
    correo = Column(String(100))
    nit = Column(String(15))
    fecha_registro = Column(DateTime, nullable=False, server_default=func.now())
    
    municipio = relationship("Municipio", back_populates="propietarios")
    tarjetas = relationship("TarjetaCirculacion", back_populates="propietario")

class Vehiculo(Base):
    __tablename__ = "vehiculo"
    id_vehiculo = Column(Integer, primary_key=True, index=True)
    vin = Column(String(17), nullable=False, unique=True)
    placa = Column(String(10), nullable=False, unique=True)
    id_tipo_vehiculo = Column(Integer, ForeignKey("tipo_vehiculo.id_tipo_vehiculo"), nullable=False)
    id_marca = Column(Integer, ForeignKey("marca_vehiculo.id_marca"), nullable=False)
    id_linea = Column(Integer, ForeignKey("linea_vehiculo.id_linea"), nullable=False)
    modelo_anio = Column(Integer, nullable=False)
    id_color = Column(Integer, ForeignKey("color.id_color"), nullable=False)
    numero_motor = Column(String(30), nullable=False)
    numero_chasis = Column(String(30), nullable=False)
    cilindros = Column(Integer)
    cilindrada_cc = Column(Integer)
    ejes = Column(Integer, nullable=False, default=2)
    tonelaje = Column(Numeric(8, 2))
    pasajeros = Column(Integer)
    combustible = Column(SQLEnum(TipoCombustibleEnum), nullable=False)
    uso = Column(SQLEnum(UsoVehiculoEnum), nullable=False, default=UsoVehiculoEnum.PARTICULAR)
    fecha_registro = Column(DateTime, nullable=False, server_default=func.now())
    
    tipo_vehiculo = relationship("TipoVehiculo", back_populates="vehiculos")
    marca = relationship("MarcaVehiculo", back_populates="vehiculos")
    linea = relationship("LineaVehiculo", back_populates="vehiculos")
    color = relationship("Color", back_populates="vehiculos")
    tarjetas = relationship("TarjetaCirculacion", back_populates="vehiculo")

class TarjetaCirculacion(Base):
    __tablename__ = "tarjeta_circulacion"
    id_tarjeta = Column(BigInteger, primary_key=True, index=True)
    id_vehiculo = Column(Integer, ForeignKey("vehiculo.id_vehiculo"), nullable=False)
    id_propietario = Column(Integer, ForeignKey("propietario.id_propietario"), nullable=False)
    numero_tarjeta = Column(String(20), nullable=False, unique=True)
    fecha_emision = Column(Date, nullable=False, server_default=func.now())
    fecha_vencimiento = Column(Date, nullable=False)
    estado = Column(SQLEnum(EstadoTarjetaEnum), nullable=False, default=EstadoTarjetaEnum.VIGENTE)
    id_usuario_emision = Column(Integer, ForeignKey("usuario_sistema.id_usuario"))
    observaciones = Column(Text)
    fecha_registro = Column(DateTime, nullable=False, server_default=func.now())
    
    vehiculo = relationship("Vehiculo", back_populates="tarjetas")
    propietario = relationship("Propietario", back_populates="tarjetas")
    usuario_emision = relationship("UsuarioSistema", back_populates="tarjetas_emitidas")
    historial = relationship("HistorialCambios", back_populates="tarjeta")
    alertas = relationship("Alerta", back_populates="tarjeta")

class HistorialCambios(Base):
    __tablename__ = "historial_cambios"
    id_historial = Column(BigInteger, primary_key=True, index=True)
    id_tarjeta = Column(BigInteger, ForeignKey("tarjeta_circulacion.id_tarjeta"), nullable=False)
    tipo_cambio = Column(SQLEnum(TipoCambioEnum), nullable=False)
    valor_anterior = Column(Text)
    valor_nuevo = Column(Text, nullable=False)
    fecha_hora = Column(DateTime, nullable=False, server_default=func.now())
    usuario_responsable = Column(Integer, ForeignKey("usuario_sistema.id_usuario"))
    
    tarjeta = relationship("TarjetaCirculacion", back_populates="historial")
    usuario_responsable_rel = relationship("UsuarioSistema", back_populates="historial_realizado")

class Alerta(Base):
    __tablename__ = "alerta"
    id_alerta = Column(BigInteger, primary_key=True, index=True)
    id_tarjeta = Column(BigInteger, ForeignKey("tarjeta_circulacion.id_tarjeta"), nullable=False)
    tipo_alerta = Column(SQLEnum(TipoAlertaEnum), nullable=False)
    fecha_generacion = Column(DateTime, nullable=False, server_default=func.now())
    estado_alerta = Column(SQLEnum(EstadoAlertaEnum), nullable=False, default=EstadoAlertaEnum.ACTIVA)
    dias_umbral = Column(Integer)
    atendida_por = Column(Integer, ForeignKey("usuario_sistema.id_usuario"))
    fecha_atencion = Column(DateTime)
    descripcion = Column(Text)
    
    tarjeta = relationship("TarjetaCirculacion", back_populates="alertas")
    usuario_atencion = relationship("UsuarioSistema", back_populates="alertas_atendidas")
