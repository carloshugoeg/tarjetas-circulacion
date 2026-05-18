# Documentacion tecnica y de uso

Sistema de Gestion de Tarjetas de Circulacion

Proyecto del curso Bases de Datos I. La aplicacion administra propietarios, vehiculos y tarjetas de circulacion, con catalogos normalizados, validaciones de dominio, API REST y una interfaz React para operar los registros.

## 1. Alcance

El sistema cubre estas operaciones:

- Consulta de dashboard con totales de tarjetas, vigentes, vencimientos proximos y alertas.
- Registro, edicion y eliminacion controlada de propietarios.
- Registro, edicion y eliminacion controlada de vehiculos.
- Registro, edicion y eliminacion controlada de tarjetas de circulacion.
- Mantenimiento administrativo: cambio de propietario, motor, color, desactivacion y reactivacion.
- Auditoria de cambios por medio de `historial_cambios`.
- Alertas administrativas asociadas a tarjetas.
- Documentacion interactiva de API en Swagger.

La prioridad del proyecto es el modelo de datos. El frontend existe para consumir y demostrar el modelo, no para reemplazar las reglas de integridad de la base.

## 2. Capturas del sistema

### Tarjetas

![Vista de tarjetas](screenshots/01-tarjetas-dashboard.png)

Pantalla principal. Muestra metricas generales, busqueda, filtro por estado y listado de tarjetas con propietario, DPI, placa, vehiculo, vencimiento y acciones.

### Propietarios

![Vista de propietarios](screenshots/02-propietarios.png)

Listado de propietarios registrados. Desde aqui se editan datos personales y se intenta eliminar registros. Si el propietario tiene tarjetas, PostgreSQL rechaza la eliminacion por llave foranea.

### Vehiculos

![Vista de vehiculos](screenshots/03-vehiculos.png)

Listado de vehiculos con placa, VIN, marca, linea, motor, color y uso. Los cambios sensibles de motor y color se hacen en la pantalla de mantenimiento para dejar auditoria.

### Mantenimiento

![Vista de mantenimiento](screenshots/04-mantenimiento.png)

Pantalla para ejecutar operaciones que generan historial: cambio de propietario, cambio de motor, cambio de color y cambio de estado.

### Auditoria

![Vista de auditoria](screenshots/05-auditoria.png)

Consulta del historial de cambios y alertas. Los valores de propietario y color se traducen desde IDs hacia datos legibles usando catalogos cargados en frontend.

### Swagger

![Swagger API](screenshots/06-swagger-api.png)

Documentacion generada por FastAPI. Lista endpoints, metodos HTTP, DTOs de entrada y schemas de respuesta.

## 3. Arquitectura

```text
React + Vite frontend
  http://localhost:5173
        |
        | fetch JSON
        v
FastAPI backend
  http://localhost:8000/api
        |
        | SQLAlchemy Session
        v
PostgreSQL 15
  contenedor: db:5432
  host: localhost:5433
```

Servicios definidos en `docker-compose.yml`:

| Servicio | Tecnologia | Puerto | Responsabilidad |
|---|---|---:|---|
| `db` | PostgreSQL 15 Alpine | `5433:5432` | Base de datos principal |
| `backend` | FastAPI + SQLAlchemy | `8000:8000` | API REST y reglas de negocio |
| `frontend` | React + Vite | `5173:5173` | Interfaz de usuario |

Variables relevantes:

```env
DATABASE_URL=postgresql://user_circulacion:password_circulacion@db:5432/circulacion_db
VITE_API_URL=http://localhost:8000/api
```

Cuando se ejecuta fuera de Docker, el backend puede apuntar a:

```env
DATABASE_URL=postgresql://user_circulacion:password_circulacion@localhost:5433/circulacion_db
```

## 4. Estructura de carpetas

```text
backend/
  api/endpoints.py              Rutas HTTP de FastAPI
  core/config.py                Lectura de variables de entorno
  core/database.py              Engine, sesiones y dependencia get_db()
  crud/crud.py                  Acceso a datos y operaciones de mantenimiento
  models/models.py              Entidades ORM SQLAlchemy
  schemas/schemas.py            DTOs Pydantic de entrada y salida
  tests/test_api_database_integrity.py

db_init/
  01_schema.sql                 Tipos ENUM, tablas y constraints
  02_seed.sql                   Catalogos iniciales
  03_sample_data.sql            Registros de prueba

frontend/
  src/api.js                    Cliente HTTP hacia FastAPI
  src/App.jsx                   Vistas, formularios y flujo de datos
  src/styles.css                Estilos

docs/
  DOCUMENTACION_TECNICA_USO.md  Este documento
  screenshots/                  Capturas usadas en la documentacion
```

## 5. Requerimientos tomados de la primera fase

La primera fase define 12 entidades:

| Grupo | Entidades |
|---|---|
| Geografia | `departamento`, `municipio` |
| Catalogos vehiculares | `tipo_vehiculo`, `marca_vehiculo`, `linea_vehiculo`, `color` |
| Actores | `usuario_sistema`, `propietario` |
| Entidades principales | `vehiculo`, `tarjeta_circulacion` |
| Auditoria y control | `historial_cambios`, `alerta` |

El modelo actual implementa esas 12 tablas en `db_init/01_schema.sql` y las representa en el ORM de `backend/models/models.py`.

Punto importante: la primera fase menciona triggers y permisos para hacer el historial inmutable desde la base. En el repo actual no hay triggers ni roles SQL para bloquear `UPDATE` o `DELETE` sobre `historial_cambios`. La auditoria se genera desde el backend en las funciones de mantenimiento. La base si protege integridad con `PRIMARY KEY`, `FOREIGN KEY`, `UNIQUE`, `CHECK` y `ENUM`.

## 6. Modelo relacional

```mermaid
erDiagram
    DEPARTAMENTO ||--o{ MUNICIPIO : contiene
    MUNICIPIO ||--o{ PROPIETARIO : residencia

    MARCA_VEHICULO ||--o{ LINEA_VEHICULO : tiene
    TIPO_VEHICULO ||--o{ VEHICULO : clasifica
    MARCA_VEHICULO ||--o{ VEHICULO : marca
    LINEA_VEHICULO ||--o{ VEHICULO : linea
    COLOR ||--o{ VEHICULO : color

    VEHICULO ||--o{ TARJETA_CIRCULACION : ampara
    PROPIETARIO ||--o{ TARJETA_CIRCULACION : posee
    USUARIO_SISTEMA ||--o{ TARJETA_CIRCULACION : emite

    TARJETA_CIRCULACION ||--o{ HISTORIAL_CAMBIOS : registra
    USUARIO_SISTEMA ||--o{ HISTORIAL_CAMBIOS : modifica

    TARJETA_CIRCULACION ||--o{ ALERTA : genera
    USUARIO_SISTEMA ||--o{ ALERTA : atiende
```

### Cardinalidades

| Relacion | Tipo | Justificacion |
|---|---|---|
| Departamento a municipio | 1:N | Un departamento contiene varios municipios |
| Municipio a propietario | 1:N | Un municipio puede tener muchos propietarios |
| Marca a linea | 1:N | Una marca tiene varias lineas |
| Catalogos vehiculares a vehiculo | 1:N | Muchos vehiculos comparten marca, linea, color y tipo |
| Vehiculo a tarjeta | 1:N | Permite historial de tarjetas por renovacion o cambio |
| Propietario a tarjeta | 1:N | Un propietario puede tener varias tarjetas |
| Tarjeta a historial | 1:N | Una tarjeta puede recibir varios cambios |
| Tarjeta a alerta | 1:N | Una tarjeta puede generar varias alertas |

## 7. Base de datos PostgreSQL

### 7.1 Tipos ENUM

Archivo: `db_init/01_schema.sql`

```sql
CREATE TYPE estado_tarjeta_enum AS ENUM (
    'VIGENTE', 'VENCIDA', 'SUSPENDIDA', 'CANCELADA'
);

CREATE TYPE tipo_combustible_enum AS ENUM (
    'GASOLINA', 'DIESEL', 'ELECTRICO', 'HIBRIDO'
);

CREATE TYPE uso_vehiculo_enum AS ENUM (
    'PARTICULAR', 'COMERCIAL', 'OFICIAL', 'DIPLOMATICO'
);
```

Los ENUM se usan cuando el dominio es cerrado. Esto aplica a estados, combustible, uso, tipo de cambio y tipo de alerta. Marcas, lineas, municipios y colores quedan en tablas porque son catalogos consultables y pueden crecer.

### 7.2 Tablas y llaves

| Tabla | PK | FKs principales | Restricciones |
|---|---|---|---|
| `departamento` | `id_departamento` | Ninguna | `nombre` unico, `codigo` unico |
| `municipio` | `id_municipio` | `id_departamento` | `UNIQUE(id_departamento, nombre)` |
| `tipo_vehiculo` | `id_tipo_vehiculo` | Ninguna | `nombre` unico |
| `marca_vehiculo` | `id_marca` | Ninguna | `nombre` unico |
| `linea_vehiculo` | `id_linea` | `id_marca` | `UNIQUE(id_marca, nombre)` |
| `color` | `id_color` | Ninguna | `nombre` unico |
| `usuario_sistema` | `id_usuario` | Ninguna | `username` unico |
| `propietario` | `id_propietario` | `id_municipio` | DPI unico, formato DPI, formato telefono |
| `vehiculo` | `id_vehiculo` | tipo, marca, linea, color | VIN unico, placa unica, checks de formato y rangos |
| `tarjeta_circulacion` | `id_tarjeta` | vehiculo, propietario, usuario | numero unico, fechas validas |
| `historial_cambios` | `id_historial` | tarjeta, usuario | tipo ENUM, valor nuevo obligatorio |
| `alerta` | `id_alerta` | tarjeta, usuario | estado consistente, dias umbral positivo |

### 7.3 Constraints importantes

Propietario:

```sql
CONSTRAINT chk_dpi_formato CHECK (dpi ~ '^\d{13}$'),
CONSTRAINT chk_telefono_formato CHECK (telefono IS NULL OR telefono ~ '^\d{8}$')
```

Vehiculo:

```sql
CONSTRAINT chk_vin_formato CHECK (vin ~ '^[A-HJ-NPR-Z0-9]{17}$'),
CONSTRAINT chk_placa_formato CHECK (placa ~ '^[A-Z]{1,2}-?\d{2,4}[A-Z]{2,3}$'),
CONSTRAINT chk_modelo_anio CHECK (modelo_anio BETWEEN 1900 AND EXTRACT(YEAR FROM CURRENT_DATE)::INT + 1),
CONSTRAINT chk_cilindros CHECK (cilindros IS NULL OR cilindros BETWEEN 1 AND 16),
CONSTRAINT chk_ejes CHECK (ejes BETWEEN 2 AND 7)
```

Tarjeta:

```sql
CONSTRAINT chk_fechas CHECK (fecha_vencimiento > fecha_emision)
```

Alerta:

```sql
CONSTRAINT chk_atencion CHECK (
    (estado_alerta = 'ACTIVA' AND atendida_por IS NULL AND fecha_atencion IS NULL)
    OR (estado_alerta IN ('ATENDIDA', 'RESUELTA'))
),
CONSTRAINT chk_dias_umbral CHECK (dias_umbral IS NULL OR dias_umbral > 0)
```

Estas reglas no dependen del frontend. Si alguien intenta insertar datos invalidos desde pgAdmin, un script o la API, PostgreSQL aplica las mismas restricciones.

### 7.4 Normalizacion

El modelo esta normalizado hasta 3FN para las entidades principales.

1FN:

- Los campos son atomicos.
- El propietario no usa un unico campo `nombre_completo`; separa `primer_nombre`, `segundo_nombre`, `primer_apellido`, `segundo_apellido`.

2FN:

- Las tablas usan PK simple `SERIAL` o `BIGSERIAL`.
- Las restricciones compuestas son `UNIQUE`, no llaves primarias compuestas.

3FN:

- `propietario` guarda `id_municipio`, no el nombre del municipio ni departamento.
- `vehiculo` guarda IDs de marca, linea, tipo y color.
- `tarjeta_circulacion` relaciona propietario y vehiculo, no duplica datos personales ni tecnicos.

Redundancias eliminadas:

- Colores en catalogo para evitar variantes como `blanco`, `Blanco`, `BLANCO`.
- Marca y linea separadas para no repetir nombres de marcas por cada vehiculo.
- Departamento y municipio separados para evitar repetir departamentos.
- Estado, uso y combustible con ENUM para proteger dominios cerrados.

## 8. Datos actuales de prueba

Consulta tomada contra el contenedor `circulacion_db`:

```text
tabla                count
------------------   -----
alerta               0
departamento         3
historial_cambios    1
municipio            5
propietario          2
tarjeta_circulacion  2
vehiculo             2
```

Tarjetas cargadas:

```text
numero_tarjeta   placa     dpi            propietario    estado    vencimiento
---------------  --------  -------------  -------------  --------  -----------
TC-2024-000001   P-123ABC  9876543210101  Maria Garcia   VIGENTE   2027-05-08
TC-2024-000002   M-456DEF  9876543210101  Maria Garcia   VIGENTE   2027-05-08
```

## 9. Backend

### 9.1 Configuracion

Archivo: `backend/core/config.py`

```python
class Settings(BaseSettings):
    DATABASE_URL: str = Field(..., description="PostgreSQL connection URL for the application database")
    PROJECT_NAME: str = "Sistema de Gestion de Tarjetas de Circulacion"
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    model_config = ConfigDict(env_file=".env")
```

La aplicacion no trae una URL de base de datos quemada. `DATABASE_URL` es obligatoria. Si no existe, el backend falla al arrancar. Es una decision correcta para no conectarse por accidente a otra base.

### 9.2 Conexion SQLAlchemy

Archivo: `backend/core/database.py`

```python
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Flujo por request:

```text
HTTP request
  -> FastAPI endpoint
  -> Depends(get_db)
  -> SessionLocal abre sesion
  -> CRUD consulta o modifica
  -> commit o rollback
  -> get_db cierra sesion
```

No se reutiliza una misma sesion global. Cada request recibe su propia sesion.

### 9.3 CORS y health check

Archivo: `backend/main.py`

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok"}
    finally:
        db.close()
```

El health check no solo revisa que FastAPI este vivo. Tambien ejecuta `SELECT 1` contra PostgreSQL. Docker Compose usa esta ruta para saber si el backend esta listo.

## 10. ORM SQLAlchemy

Archivo: `backend/models/models.py`

Los modelos ORM representan las tablas. Cada clase hereda de `Base` y declara `__tablename__`.

### 10.1 ENUMs en Python

```python
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
```

El backend usa los mismos valores que PostgreSQL. Esto evita que Pydantic acepte estados que la base rechazaria.

### 10.2 Propietario

```python
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
```

Relacion directa:

- `Propietario.municipio` permite navegar al municipio.
- `Propietario.tarjetas` permite obtener tarjetas asociadas al propietario.

### 10.3 Vehiculo

```python
class Vehiculo(Base):
    __tablename__ = "vehiculo"
    id_vehiculo = Column(Integer, primary_key=True, index=True)
    vin = Column(String(17), nullable=False, unique=True)
    placa = Column(String(10), nullable=False, unique=True)
    id_tipo_vehiculo = Column(Integer, ForeignKey("tipo_vehiculo.id_tipo_vehiculo"), nullable=False)
    id_marca = Column(Integer, ForeignKey("marca_vehiculo.id_marca"), nullable=False)
    id_linea = Column(Integer, ForeignKey("linea_vehiculo.id_linea"), nullable=False)
    id_color = Column(Integer, ForeignKey("color.id_color"), nullable=False)
    combustible = Column(SQLEnum(TipoCombustibleEnum), nullable=False)
    uso = Column(SQLEnum(UsoVehiculoEnum), nullable=False, default=UsoVehiculoEnum.PARTICULAR)

    tipo_vehiculo = relationship("TipoVehiculo", back_populates="vehiculos")
    marca = relationship("MarcaVehiculo", back_populates="vehiculos")
    linea = relationship("LineaVehiculo", back_populates="vehiculos")
    color = relationship("Color", back_populates="vehiculos")
    tarjetas = relationship("TarjetaCirculacion", back_populates="vehiculo")
```

El vehiculo tiene varias FKs porque el modelo evita textos libres. Eso permite reportes y filtros confiables por marca, linea, color, uso o tipo.

### 10.4 Tarjeta de circulacion

```python
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
```

Esta es la entidad central. Relaciona propietario y vehiculo. El propietario actual del vehiculo dentro del sistema se obtiene por la tarjeta vigente.

### 10.5 Historial y alertas

```python
class HistorialCambios(Base):
    __tablename__ = "historial_cambios"
    id_historial = Column(BigInteger, primary_key=True, index=True)
    id_tarjeta = Column(BigInteger, ForeignKey("tarjeta_circulacion.id_tarjeta"), nullable=False)
    tipo_cambio = Column(SQLEnum(TipoCambioEnum), nullable=False)
    valor_anterior = Column(Text)
    valor_nuevo = Column(Text, nullable=False)
    fecha_hora = Column(DateTime, nullable=False, server_default=func.now())
    usuario_responsable = Column(Integer, ForeignKey("usuario_sistema.id_usuario"))
```

```python
class Alerta(Base):
    __tablename__ = "alerta"
    id_alerta = Column(BigInteger, primary_key=True, index=True)
    id_tarjeta = Column(BigInteger, ForeignKey("tarjeta_circulacion.id_tarjeta"), nullable=False)
    tipo_alerta = Column(SQLEnum(TipoAlertaEnum), nullable=False)
    fecha_generacion = Column(DateTime, nullable=False, server_default=func.now())
    estado_alerta = Column(SQLEnum(EstadoAlertaEnum), nullable=False, default=EstadoAlertaEnum.ACTIVA)
    atendida_por = Column(Integer, ForeignKey("usuario_sistema.id_usuario"))
    fecha_atencion = Column(DateTime)
    descripcion = Column(Text)
```

El historial almacena cambios. La alerta almacena eventos administrativos o de control.

## 11. DTOs y validacion Pydantic

Archivo: `backend/schemas/schemas.py`

Los DTOs separan tres casos:

- `Base`: campos comunes.
- `Create`: datos necesarios para crear.
- `Update`: campos opcionales para `PATCH`.
- Respuesta final: incluye ID y `model_config = ConfigDict(from_attributes=True)`.

### 11.1 PropietarioCreate

```python
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
```

El frontend puede mandar JSON, pero Pydantic valida formato antes de intentar insertar.

### 11.2 VehiculoCreate

```python
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
    combustible: TipoCombustibleEnum
    uso: UsoVehiculoEnum = UsoVehiculoEnum.PARTICULAR

    @field_validator("modelo_anio")
    @classmethod
    def validate_modelo_anio(cls, value: int):
        max_year = date.today().year + 1
        if value < 1900 or value > max_year:
            raise ValueError(f"modelo_anio debe estar entre 1900 y {max_year}")
        return value
```

Validaciones:

- VIN de 17 caracteres sin I, O, Q.
- Placa con formato esperado.
- Año entre 1900 y el siguiente año calendario.
- Combustible y uso limitados por ENUM.

### 11.3 TarjetaCirculacionCreate

```python
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
```

La regla tambien existe en PostgreSQL con `chk_fechas`. La validacion duplicada es intencional:

- Pydantic devuelve error rapido al cliente.
- PostgreSQL conserva la proteccion definitiva.

### 11.4 DTOs de mantenimiento

```python
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
```

Estos DTOs evitan usar formularios ambiguos. Cada operacion de mantenimiento tiene un contrato especifico.

## 12. CRUD y transacciones

Archivo: `backend/crud/crud.py`

### 12.1 Patron de creacion

```python
def create_propietario(db: Session, propietario: schemas.PropietarioCreate):
    db_propietario = models.Propietario(**propietario.model_dump())
    db.add(db_propietario)
    db.commit()
    db.refresh(db_propietario)
    return db_propietario
```

Pasos:

1. El DTO se convierte a diccionario con `model_dump()`.
2. SQLAlchemy crea la entidad ORM.
3. `db.add()` agrega la entidad a la sesion.
4. `db.commit()` confirma la transaccion.
5. `db.refresh()` trae valores generados por la base, por ejemplo ID y fechas.

### 12.2 Actualizacion parcial

```python
def apply_updates(db_obj, values: dict):
    for key, value in values.items():
        setattr(db_obj, key, value)
    return db_obj

def update_propietario(db: Session, propietario_id: int, propietario: schemas.PropietarioUpdate):
    db_propietario = get_propietario(db, propietario_id)
    if not db_propietario:
        return None
    apply_updates(db_propietario, propietario.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(db_propietario)
    return db_propietario
```

`exclude_unset=True` es clave. Si el cliente solo manda `telefono`, los demas campos no se reemplazan por `None`.

### 12.3 Dashboard

```python
def get_dashboard_summary(db: Session):
    today = date.today()
    soon = today + timedelta(days=30)
    total_tarjetas = db.query(models.TarjetaCirculacion).count()
    vigentes = db.query(models.TarjetaCirculacion).filter(
        models.TarjetaCirculacion.estado == models.EstadoTarjetaEnum.VIGENTE
    ).count()
    proximas = db.query(models.TarjetaCirculacion).filter(
        models.TarjetaCirculacion.fecha_vencimiento >= today,
        models.TarjetaCirculacion.fecha_vencimiento <= soon,
    ).count()
```

Este metodo alimenta las metricas del frontend.

### 12.4 Auditoria de cambios

```python
def log_cambio(db: Session, tarjeta_id: int, tipo: models.TipoCambioEnum, anterior: str, nuevo: str, usuario_id: int = None):
    db_historial = models.HistorialCambios(
        id_tarjeta=tarjeta_id,
        tipo_cambio=tipo,
        valor_anterior=anterior,
        valor_nuevo=nuevo,
        usuario_responsable=usuario_id
    )
    db.add(db_historial)
```

`log_cambio()` no hace commit por si sola. Se ejecuta dentro de la misma transaccion de la operacion principal. Si falla el cambio, no queda historial separado.

## 13. Endpoints

Archivo: `backend/api/endpoints.py`

### 13.1 Grupos

| Grupo | Ruta base | Uso |
|---|---|---|
| Dashboard | `/api/resumen/` | Metricas generales |
| Usuarios | `/api/usuarios/` | Operadores del sistema |
| Propietarios | `/api/propietarios/` | CRUD de propietarios |
| Vehiculos | `/api/vehiculos/` | CRUD de vehiculos |
| Tarjetas | `/api/tarjetas/` | CRUD de tarjetas |
| Mantenimiento | rutas `PATCH` especificas | Cambios con auditoria |
| Catalogos | `/api/catalogos/...` | Lectura de catalogos |
| Auditoria | `/api/historial/`, `/api/alertas/` | Consulta de control |

### 13.2 Metodos principales

| Metodo | Ruta | Body | Respuesta |
|---|---|---|---|
| `GET` | `/api/resumen/` | No | Totales del dashboard |
| `GET` | `/api/propietarios/?limit=500` | No | Lista de propietarios |
| `POST` | `/api/propietarios/` | `PropietarioCreate` | Propietario creado |
| `PATCH` | `/api/propietarios/{id}` | `PropietarioUpdate` | Propietario actualizado |
| `DELETE` | `/api/propietarios/{id}` | No | `204` si se elimina |
| `GET` | `/api/vehiculos/?limit=500` | No | Lista de vehiculos |
| `POST` | `/api/vehiculos/` | `VehiculoCreate` | Vehiculo creado |
| `PATCH` | `/api/vehiculos/{id}` | `VehiculoUpdate` | Vehiculo actualizado |
| `DELETE` | `/api/vehiculos/{id}` | No | `204` si se elimina |
| `GET` | `/api/tarjetas/?limit=500` | No | Lista de tarjetas |
| `POST` | `/api/tarjetas/` | `TarjetaCirculacionCreate` | Tarjeta creada |
| `PATCH` | `/api/tarjetas/{id}` | `TarjetaCirculacionUpdate` | Tarjeta actualizada |
| `DELETE` | `/api/tarjetas/{id}` | No | `204` si se elimina |
| `PATCH` | `/api/tarjetas/{id}/cambio-propietario` | `CambioPropietarioRequest` | Tarjeta actualizada |
| `PATCH` | `/api/vehiculos/{id}/cambio-motor` | `CambioMotorRequest` | Vehiculo actualizado |
| `PATCH` | `/api/vehiculos/{id}/cambio-color` | `CambioColorRequest` | Vehiculo actualizado |
| `PATCH` | `/api/tarjetas/{id}/desactivar` | `DesactivarTarjetaRequest` | Tarjeta desactivada |
| `PATCH` | `/api/tarjetas/{id}/reactivar` | `ReactivarTarjetaRequest` | Tarjeta vigente |

### 13.3 Manejo de errores

```python
def commit_error_to_http(exc: IntegrityError):
    raise HTTPException(status_code=409, detail="Conflicto de integridad en la base de datos")
```

Codigos usados:

| Codigo | Caso |
|---:|---|
| `201` | Creacion correcta |
| `204` | Eliminacion correcta sin body |
| `400` | Regla de negocio invalida |
| `404` | Recurso no encontrado |
| `409` | Conflicto de integridad, duplicado o FK protegida |
| `422` | Error de validacion Pydantic |

Ejemplo: si se intenta borrar un vehiculo con tarjetas asociadas, PostgreSQL rechaza la operacion y el endpoint devuelve:

```python
raise HTTPException(status_code=409, detail="No se puede eliminar: el vehiculo tiene tarjetas asociadas")
```

### 13.4 Validacion marca-linea

```python
def validate_linea_marca(db: Session, marca_id: int, linea_id: int):
    if not crud.linea_belongs_to_marca(db, linea_id=linea_id, marca_id=marca_id):
        raise HTTPException(status_code=400, detail="La linea no pertenece a la marca seleccionada")
```

Esta regla corrige un problema comun: `vehiculo` tiene `id_marca` e `id_linea`. Sin validacion, se podria guardar `Toyota` con linea `Civic`. La FK solo valida que ambos IDs existan; esta funcion valida que sean coherentes entre si.

## 14. Flujos de negocio

### 14.1 Crear propietario

```text
Frontend
  -> POST /api/propietarios/
  -> PropietarioCreate valida DPI y telefono
  -> endpoint revisa DPI duplicado
  -> CRUD inserta en propietario
  -> PostgreSQL valida FK id_municipio
  -> respuesta JSON con id_propietario
```

JSON de ejemplo:

```json
{
  "dpi": "1234567890101",
  "primer_nombre": "Ana",
  "primer_apellido": "Lopez",
  "fecha_nacimiento": "1990-01-01",
  "direccion": "Zona 1",
  "id_municipio": 1,
  "telefono": "12345678",
  "correo": "ana@example.com",
  "nit": "CF"
}
```

### 14.2 Crear vehiculo

```text
Frontend
  -> POST /api/vehiculos/
  -> VehiculoCreate valida VIN, placa, anio, enums
  -> endpoint valida que linea pertenezca a marca
  -> endpoint revisa VIN duplicado
  -> endpoint revisa placa duplicada
  -> CRUD inserta en vehiculo
  -> PostgreSQL valida FKs y checks
```

JSON de ejemplo:

```json
{
  "vin": "1HGCM82633A004352",
  "placa": "P123ABC",
  "id_tipo_vehiculo": 1,
  "id_marca": 1,
  "id_linea": 1,
  "modelo_anio": 2022,
  "id_color": 1,
  "numero_motor": "MOTOR-1",
  "numero_chasis": "CHASIS-1",
  "ejes": 2,
  "combustible": "GASOLINA",
  "uso": "PARTICULAR"
}
```

### 14.3 Crear tarjeta

```text
Frontend
  -> POST /api/tarjetas/
  -> TarjetaCirculacionCreate valida fechas
  -> endpoint revisa numero_tarjeta duplicado
  -> CRUD inserta en tarjeta_circulacion
  -> PostgreSQL valida vehiculo, propietario y usuario emisor
```

JSON de ejemplo:

```json
{
  "id_vehiculo": 1,
  "id_propietario": 1,
  "numero_tarjeta": "TC-2026-000001",
  "fecha_emision": "2026-05-11",
  "fecha_vencimiento": "2027-05-11",
  "estado": "VIGENTE",
  "id_usuario_emision": 1,
  "observaciones": "Emision inicial"
}
```

### 14.4 Cambio de propietario

Ruta:

```text
PATCH /api/tarjetas/{tarjeta_id}/cambio-propietario
```

Body:

```json
{
  "nuevo_propietario_id": 2,
  "usuario_id": 1
}
```

Funcion principal:

```python
def update_propietario_tarjeta(db: Session, tarjeta_id: int, nuevo_propietario_id: int, usuario_id: int = None):
    db_tarjeta = get_tarjeta(db, tarjeta_id)
    if not db_tarjeta:
        return None

    valor_anterior = str(db_tarjeta.id_propietario)
    db_tarjeta.id_propietario = nuevo_propietario_id

    log_cambio(db, tarjeta_id, models.TipoCambioEnum.PROPIETARIO, valor_anterior, str(nuevo_propietario_id), usuario_id)

    db.commit()
    db.refresh(db_tarjeta)
    return db_tarjeta
```

Resultado en base:

- Actualiza `tarjeta_circulacion.id_propietario`.
- Inserta fila en `historial_cambios` con `tipo_cambio = PROPIETARIO`.

### 14.5 Cambio de motor

Ruta:

```text
PATCH /api/vehiculos/{vehiculo_id}/cambio-motor
```

Body:

```json
{
  "nuevo_motor": "MOTOR-2",
  "usuario_id": 1
}
```

La operacion actualiza `vehiculo.numero_motor`. Si existe una tarjeta vigente para ese vehiculo, registra historial tipo `MOTOR`.

```python
db_tarjeta = get_vigente_tarjeta_by_vehiculo(db, vehiculo_id)

if db_tarjeta:
    log_cambio(db, db_tarjeta.id_tarjeta, models.TipoCambioEnum.MOTOR, valor_anterior, nuevo_motor, usuario_id)
```

### 14.6 Cambio de color

Ruta:

```text
PATCH /api/vehiculos/{vehiculo_id}/cambio-color
```

Body:

```json
{
  "nuevo_color_id": 2,
  "usuario_id": 1
}
```

Validaciones:

- El vehiculo existe.
- El color existe.
- El color nuevo no es el mismo actual.

Despues:

- Actualiza `vehiculo.id_color`.
- Registra `historial_cambios` tipo `COLOR` si hay tarjeta vigente.

### 14.7 Desactivar tarjeta

Ruta:

```text
PATCH /api/tarjetas/{tarjeta_id}/desactivar
```

Body:

```json
{
  "nuevo_estado": "SUSPENDIDA",
  "motivo": "Suspension administrativa",
  "usuario_id": 1
}
```

Funcion:

```python
def deactivate_tarjeta(db: Session, tarjeta_id: int, nuevo_estado: models.EstadoTarjetaEnum, motivo: str = None, usuario_id: int = None):
    db_tarjeta = get_tarjeta(db, tarjeta_id)
    if not db_tarjeta:
        return None

    valor_anterior = db_tarjeta.estado.value
    db_tarjeta.estado = nuevo_estado
    db_tarjeta.observaciones = append_observation(db_tarjeta.observaciones, "Motivo desactivacion", motivo)

    log_cambio(db, tarjeta_id, models.TipoCambioEnum.ESTADO, valor_anterior, nuevo_estado.value, usuario_id)

    if nuevo_estado in (models.EstadoTarjetaEnum.SUSPENDIDA, models.EstadoTarjetaEnum.CANCELADA):
        tipo_alerta = models.TipoAlertaEnum.SUSPENSION_ADMINISTRATIVA
        if "impago" in (motivo or "").lower():
            tipo_alerta = models.TipoAlertaEnum.IMPAGO

        db_alerta = models.Alerta(
            id_tarjeta=tarjeta_id,
            tipo_alerta=tipo_alerta,
            descripcion=motivo
        )
        db.add(db_alerta)
```

Efecto:

- Cambia estado de tarjeta.
- Agrega motivo a observaciones.
- Registra historial.
- Crea alerta si el estado pasa a `SUSPENDIDA` o `CANCELADA`.

### 14.8 Reactivar tarjeta

Ruta:

```text
PATCH /api/tarjetas/{tarjeta_id}/reactivar
```

Body:

```json
{
  "motivo": "Pago completado",
  "usuario_id": 1
}
```

Efecto:

- Cambia `estado` a `VIGENTE`.
- Registra historial tipo `ESTADO`.
- Marca alertas activas de esa tarjeta como `RESUELTA`.
- Guarda `fecha_atencion` y `atendida_por`.

## 15. Frontend

### 15.1 Cliente API

Archivo: `frontend/src/api.js`

```javascript
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    let message = "No se pudo completar la solicitud";
    try {
      const body = await response.json();
      message = body.detail || message;
    } catch {
      message = response.statusText || message;
    }
    throw new Error(Array.isArray(message) ? message.map((item) => item.msg).join(", ") : message);
  }

  if (response.status === 204) return null;
  return response.json();
}
```

El frontend no arma URLs en cada componente. Todas las llamadas pasan por `api.js`.

### 15.2 Mapa de peticiones desde frontend

```javascript
export const api = {
  getResumen: () => request("/resumen/"),
  getPropietarios: () => request("/propietarios/?limit=500"),
  getVehiculos: () => request("/vehiculos/?limit=500"),
  getTarjetas: () => request("/tarjetas/?limit=500"),
  getUsuarios: () => request("/usuarios/?limit=500"),
  getHistorial: () => request("/historial/?limit=100"),
  getAlertas: () => request("/alertas/?limit=100"),
  getCatalogo: (name, params = "") => request(`/catalogos/${name}/${params}`),
  createPropietario: (payload) => request("/propietarios/", { method: "POST", body: JSON.stringify(payload) }),
  updatePropietario: (id, payload) => request(`/propietarios/${id}`, { method: "PATCH", body: JSON.stringify(payload) }),
  deletePropietario: (id) => request(`/propietarios/${id}`, { method: "DELETE" }),
  cambioMotor: (vehiculoId, motor) =>
    request(`/vehiculos/${vehiculoId}/cambio-motor`, {
      method: "PATCH",
      body: JSON.stringify({ nuevo_motor: motor }),
    }),
};
```

Cada metodo representa una peticion concreta al backend.

### 15.3 Carga inicial de datos

Archivo: `frontend/src/App.jsx`

```javascript
const [
  resumen,
  propietarios,
  vehiculos,
  tarjetas,
  usuarios,
  historial,
  alertas,
  departamentos,
  municipios,
  tipos,
  marcas,
  lineas,
  colores,
] = await Promise.all([
  api.getResumen(),
  api.getPropietarios(),
  api.getVehiculos(),
  api.getTarjetas(),
  api.getUsuarios(),
  api.getHistorial(),
  api.getAlertas(),
  api.getCatalogo("departamentos"),
  api.getCatalogo("municipios"),
  api.getCatalogo("tipos-vehiculo"),
  api.getCatalogo("marcas"),
  api.getCatalogo("lineas"),
  api.getCatalogo("colores"),
]);
```

El frontend carga todo en paralelo para evitar una pantalla lenta. Esto funciona porque son consultas independientes.

### 15.4 Lookups por ID

```javascript
const by = (items, key) => Object.fromEntries(items.map((item) => [item[key], item]));

return {
  propietarios: by(data.propietarios, "id_propietario"),
  vehiculos: by(data.vehiculos, "id_vehiculo"),
  tarjetas: by(data.tarjetas, "id_tarjeta"),
  usuarios: by(data.usuarios, "id_usuario"),
  municipios: by(catalogs.municipios, "id_municipio"),
  marcas: by(catalogs.marcas, "id_marca"),
  lineas: by(catalogs.lineas, "id_linea"),
  colores: by(catalogs.colores, "id_color"),
};
```

La API devuelve IDs. El frontend usa mapas para mostrar nombres:

- `id_propietario` a nombre completo y DPI.
- `id_vehiculo` a placa, marca y linea.
- `id_color` a nombre de color.
- `id_municipio` a nombre de municipio.

### 15.5 Conversor de formularios

```javascript
const numericPayloadFields = new Set(["modelo_anio", "cilindros", "cilindrada_cc", "ejes", "pasajeros", "tonelaje"]);

function compactPayload(payload) {
  return Object.fromEntries(
    Object.entries(payload).map(([key, value]) => {
      if (value === "") return [key, null];
      if (key.startsWith("id_") || numericPayloadFields.has(key)) {
        return [key, value === null ? null : Number(value)];
      }
      return [key, value];
    })
  );
}
```

HTML entrega valores como string. El backend espera enteros en IDs y campos numericos. `compactPayload()` corrige eso antes de mandar el JSON.

## 16. Conexion frontend, backend y base

Ejemplo completo: crear vehiculo.

```text
Usuario llena formulario de vehiculo
  -> App.jsx arma FormData
  -> compactPayload convierte IDs y numeros
  -> api.createVehiculo(payload)
  -> fetch POST http://localhost:8000/api/vehiculos/
  -> FastAPI recibe VehiculoCreate
  -> Pydantic valida formato
  -> endpoint valida marca-linea, VIN y placa duplicada
  -> crud.create_vehiculo()
  -> SQLAlchemy INSERT INTO vehiculo
  -> PostgreSQL valida FKs, UNIQUE y CHECK
  -> commit
  -> respuesta JSON
  -> frontend recarga listas con loadData()
```

Ejemplo completo: suspender tarjeta.

```text
Usuario selecciona tarjeta
  -> frontend envia PATCH /api/tarjetas/{id}/desactivar
  -> DTO valida nuevo_estado
  -> endpoint impide usar VIGENTE en ruta de desactivacion
  -> CRUD cambia estado
  -> CRUD agrega observacion
  -> CRUD inserta historial_cambios
  -> CRUD crea alerta si aplica
  -> commit unico para todo
  -> frontend recarga tarjetas, historial y alertas
```

## 17. Uso del sistema

### 17.1 Ejecutar con Docker

Desde la raiz del proyecto:

```bash
docker compose up --build
```

Abrir:

```text
Frontend: http://localhost:5173
Backend:  http://localhost:8000
Swagger:  http://localhost:8000/docs
DB host:  localhost:5433
```

### 17.2 Ejecutar backend y frontend sin Docker

Base de datos con Docker:

```bash
docker compose up -d db
```

Backend:

```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

### 17.3 Flujo de uso recomendado

1. Abrir `http://localhost:5173`.
2. Revisar la pantalla de tarjetas.
3. Crear o editar propietarios desde `Propietarios`.
4. Crear o editar vehiculos desde `Vehiculos`.
5. Crear tarjetas desde `Tarjetas`.
6. Hacer cambios administrativos desde `Mantenimiento`.
7. Revisar efectos en `Auditoria`.
8. Revisar contratos de API en `http://localhost:8000/docs`.

### 17.4 Reglas visibles para el usuario

- Una tarjeta no puede vencer antes o el mismo dia de su emision.
- Un DPI debe tener 13 digitos.
- Un telefono debe tener 8 digitos si se ingresa.
- VIN y placa no pueden repetirse.
- Numero de tarjeta no puede repetirse.
- La linea seleccionada debe pertenecer a la marca seleccionada.
- No se puede eliminar un propietario, vehiculo o tarjeta si otra tabla lo referencia.
- Los cambios de motor, color, propietario y estado deben hacerse desde mantenimiento para dejar historial.

## 18. Pruebas

Archivo: `backend/tests/test_api_database_integrity.py`

Las pruebas usan `TEST_DATABASE_URL`. Si no existe, se omiten:

```python
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    pytest.skip("Set TEST_DATABASE_URL to run PostgreSQL integration tests.", allow_module_level=True)
```

Esto evita destruir la base principal. La fixture hace:

```python
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
seed_reference_data(db)
```

Pruebas cubiertas:

| Prueba | Verifica |
|---|---|
| `test_partial_resource_updates_use_patch_and_preserve_unspecified_fields` | `PATCH` no borra campos no enviados |
| `test_delete_returns_204_with_empty_body` | DELETE devuelve 204 sin body |
| `test_maintenance_transitions_use_patch_json_body_and_write_audit` | Cambio de motor genera historial |
| `test_duplicate_tarjeta_returns_conflict_and_session_recovers` | Duplicado devuelve 409 y la sesion sigue usable |
| `test_vehicle_line_must_belong_to_selected_brand` | Linea debe pertenecer a marca |
| `test_vehicle_year_is_validated_before_database_commit` | Anio invalido devuelve 422 |
| `test_tarjeta_requires_expiration_after_issue_date` | Fechas invalidas se rechazan |
| `test_partial_tarjeta_date_update_checks_existing_issue_date` | PATCH de fecha se valida contra fecha existente |

Comandos:

```bash
python -m compileall backend

cd frontend
npm run build
```

Pruebas de integracion:

```bash
TEST_DATABASE_URL=postgresql://user_circulacion:password_circulacion@localhost:5433/circulacion_test_db python -m pytest backend/tests
```

La base `circulacion_test_db` debe existir antes de ejecutar esa prueba.

## 19. Consultas utiles para revisar la base

Listar tablas:

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
```

Ver tarjetas con propietario y vehiculo:

```sql
SELECT
  tc.numero_tarjeta,
  v.placa,
  p.dpi,
  p.primer_nombre || ' ' || p.primer_apellido AS propietario,
  tc.estado,
  tc.fecha_vencimiento
FROM tarjeta_circulacion tc
JOIN vehiculo v ON v.id_vehiculo = tc.id_vehiculo
JOIN propietario p ON p.id_propietario = tc.id_propietario
ORDER BY tc.id_tarjeta;
```

Ver historial:

```sql
SELECT
  h.id_historial,
  tc.numero_tarjeta,
  h.tipo_cambio,
  h.valor_anterior,
  h.valor_nuevo,
  h.fecha_hora
FROM historial_cambios h
JOIN tarjeta_circulacion tc ON tc.id_tarjeta = h.id_tarjeta
ORDER BY h.fecha_hora DESC;
```

Ver alertas activas:

```sql
SELECT
  a.id_alerta,
  tc.numero_tarjeta,
  a.tipo_alerta,
  a.estado_alerta,
  a.descripcion,
  a.fecha_generacion
FROM alerta a
JOIN tarjeta_circulacion tc ON tc.id_tarjeta = a.id_tarjeta
WHERE a.estado_alerta = 'ACTIVA'
ORDER BY a.fecha_generacion DESC;
```

## 20. Puntos tecnicos fuertes

- Modelo con 12 tablas separadas por responsabilidad.
- Catalogos normalizados para evitar duplicacion.
- ENUMs para dominios cerrados.
- CHECK constraints para DPI, telefono, VIN, placa, fechas y rangos.
- FKs para impedir datos huerfanos.
- API con DTOs claros para crear, actualizar y mantener.
- Validacion duplicada donde conviene: Pydantic para respuesta rapida y PostgreSQL como proteccion final.
- Transacciones de mantenimiento que actualizan entidad y escriben auditoria juntas.
- Frontend desacoplado por `api.js`.
- Swagger disponible para revisar contratos.
- Pruebas enfocadas en integridad y reglas de API.

## 21. Limitaciones tecnicas actuales

- No hay autenticacion real. `usuario_sistema` funciona como referencia administrativa.
- No hay roles SQL ni permisos que hagan inmutable `historial_cambios`.
- No hay triggers en PostgreSQL para auditoria automatica. La auditoria depende de que los cambios pasen por las rutas de mantenimiento.
- No hay migraciones con Alembic. El schema se aplica desde `db_init/01_schema.sql`.
- No hay restriccion parcial para impedir mas de una tarjeta `VIGENTE` por vehiculo.
- No hay paginacion real en frontend; se pide `limit=500`.
- La API no hace joins para devolver vistas enriquecidas; el frontend resuelve nombres con lookups.

## 22. Mejoras recomendadas para segunda fase

- Agregar autenticacion y roles.
- Crear migraciones con Alembic.
- Implementar trigger de auditoria para cambios criticos directos en base.
- Crear indice parcial para una sola tarjeta vigente por vehiculo:

```sql
CREATE UNIQUE INDEX uq_vehiculo_tarjeta_vigente
ON tarjeta_circulacion (id_vehiculo)
WHERE estado = 'VIGENTE';
```

- Agregar indices para busquedas por `dpi`, `placa`, `vin`, `numero_tarjeta` y `estado`.
- Agregar endpoints de reportes por departamento, tipo de vehiculo y estado.
- Separar respuestas enriquecidas, por ejemplo `TarjetaDetalle`, para no resolver tantos IDs en frontend.
- Agregar tests para desactivacion, reactivacion y alertas.
- Definir comportamiento formal para tarjetas vencidas automaticas.

