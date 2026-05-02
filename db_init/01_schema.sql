-- ============================================================
-- TIPOS ENUMERADOS
-- ============================================================

CREATE TYPE tipo_cambio_enum AS ENUM (
    'PROPIETARIO', 'MOTOR', 'COLOR', 'ESTADO', 'PLACA'
);

CREATE TYPE tipo_alerta_enum AS ENUM (
    'VENCIMIENTO_PROXIMO', 'IMPAGO', 'SUSPENSION_ADMINISTRATIVA'
);

CREATE TYPE estado_alerta_enum AS ENUM (
    'ACTIVA', 'ATENDIDA', 'RESUELTA'
);

CREATE TYPE estado_tarjeta_enum AS ENUM (
    'VIGENTE', 'VENCIDA', 'SUSPENDIDA', 'CANCELADA'
);

CREATE TYPE tipo_combustible_enum AS ENUM (
    'GASOLINA', 'DIESEL', 'ELECTRICO', 'HIBRIDO'
);

CREATE TYPE uso_vehiculo_enum AS ENUM (
    'PARTICULAR', 'COMERCIAL', 'OFICIAL', 'DIPLOMATICO'
);

-- ============================================================
-- TABLAS DE REFERENCIA GEOGRAFICA
-- ============================================================

CREATE TABLE departamento (
    id_departamento SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    codigo CHAR(2) NOT NULL UNIQUE
);

CREATE TABLE municipio (
    id_municipio SERIAL PRIMARY KEY,
    id_departamento INT NOT NULL REFERENCES departamento(id_departamento),
    nombre VARCHAR(80) NOT NULL,
    UNIQUE (id_departamento, nombre)
);

-- ============================================================
-- CATALOGOS DE VEHICULOS
-- ============================================================

CREATE TABLE tipo_vehiculo (
    id_tipo_vehiculo SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT
);

CREATE TABLE marca_vehiculo (
    id_marca SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE linea_vehiculo (
    id_linea SERIAL PRIMARY KEY,
    id_marca INT NOT NULL REFERENCES marca_vehiculo(id_marca),
    nombre VARCHAR(80) NOT NULL,
    UNIQUE (id_marca, nombre)
);

CREATE TABLE color (
    id_color SERIAL PRIMARY KEY,
    nombre VARCHAR(30) NOT NULL UNIQUE
);

-- ============================================================
-- USUARIOS DEL SISTEMA
-- ============================================================

CREATE TABLE usuario_sistema (
    id_usuario SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    nombre_completo VARCHAR(150) NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- PROPIETARIO
-- ============================================================

CREATE TABLE propietario (
    id_propietario SERIAL PRIMARY KEY,
    dpi CHAR(13) NOT NULL UNIQUE,
    primer_nombre VARCHAR(50) NOT NULL,
    segundo_nombre VARCHAR(50),
    primer_apellido VARCHAR(50) NOT NULL,
    segundo_apellido VARCHAR(50),
    fecha_nacimiento DATE NOT NULL,
    direccion VARCHAR(200) NOT NULL,
    id_municipio INT NOT NULL REFERENCES municipio(id_municipio),
    telefono VARCHAR(15),
    correo VARCHAR(100),
    nit VARCHAR(15),
    fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_dpi_formato CHECK (dpi ~ '^\d{13}$'),
    CONSTRAINT chk_telefono_formato CHECK (telefono IS NULL OR telefono ~ '^\d{8}$')
);

-- ============================================================
-- VEHICULO
-- ============================================================

CREATE TABLE vehiculo (
    id_vehiculo SERIAL PRIMARY KEY,
    vin VARCHAR(17) NOT NULL UNIQUE,
    placa VARCHAR(10) NOT NULL UNIQUE,
    id_tipo_vehiculo INT NOT NULL REFERENCES tipo_vehiculo(id_tipo_vehiculo),
    id_marca INT NOT NULL REFERENCES marca_vehiculo(id_marca),
    id_linea INT NOT NULL REFERENCES linea_vehiculo(id_linea),
    modelo_anio INT NOT NULL,
    id_color INT NOT NULL REFERENCES color(id_color),
    numero_motor VARCHAR(30) NOT NULL,
    numero_chasis VARCHAR(30) NOT NULL,
    cilindros INT,
    cilindrada_cc INT,
    ejes INT NOT NULL DEFAULT 2,
    tonelaje NUMERIC(8,2),
    pasajeros INT,
    combustible tipo_combustible_enum NOT NULL,
    uso uso_vehiculo_enum NOT NULL DEFAULT 'PARTICULAR',
    fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_vin_formato CHECK (vin ~ '^[A-HJ-NPR-Z0-9]{17}$'),
    CONSTRAINT chk_placa_formato CHECK (placa ~ '^[A-Z]{1,2}-?\d{2,4}[A-Z]{2,3}$'),
    CONSTRAINT chk_modelo_anio CHECK (modelo_anio BETWEEN 1900 AND EXTRACT(YEAR FROM CURRENT_DATE)::INT + 1),
    CONSTRAINT chk_cilindros CHECK (cilindros IS NULL OR cilindros BETWEEN 1 AND 16),
    CONSTRAINT chk_ejes CHECK (ejes BETWEEN 2 AND 7)
);

-- ============================================================
-- TARJETA DE CIRCULACION
-- ============================================================

CREATE TABLE tarjeta_circulacion (
    id_tarjeta BIGSERIAL PRIMARY KEY,
    id_vehiculo INT NOT NULL REFERENCES vehiculo(id_vehiculo),
    id_propietario INT NOT NULL REFERENCES propietario(id_propietario),
    numero_tarjeta VARCHAR(20) NOT NULL UNIQUE,
    fecha_emision DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_vencimiento DATE NOT NULL,
    estado estado_tarjeta_enum NOT NULL DEFAULT 'VIGENTE',
    id_usuario_emision INT REFERENCES usuario_sistema(id_usuario),
    observaciones TEXT,
    fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_fechas CHECK (fecha_vencimiento > fecha_emision)
);

-- ============================================================
-- HISTORIAL DE CAMBIOS (Auditoria)
-- ============================================================

CREATE TABLE historial_cambios (
    id_historial BIGSERIAL PRIMARY KEY,
    id_tarjeta BIGINT NOT NULL REFERENCES tarjeta_circulacion(id_tarjeta),
    tipo_cambio tipo_cambio_enum NOT NULL,
    valor_anterior TEXT,
    valor_nuevo TEXT NOT NULL,
    fecha_hora TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    usuario_responsable INT REFERENCES usuario_sistema(id_usuario)
);

-- ============================================================
-- ALERTAS
-- ============================================================

CREATE TABLE alerta (
    id_alerta BIGSERIAL PRIMARY KEY,
    id_tarjeta BIGINT NOT NULL REFERENCES tarjeta_circulacion(id_tarjeta),
    tipo_alerta tipo_alerta_enum NOT NULL,
    fecha_generacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado_alerta estado_alerta_enum NOT NULL DEFAULT 'ACTIVA',
    dias_umbral INT,
    atendida_por INT REFERENCES usuario_sistema(id_usuario),
    fecha_atencion TIMESTAMP,
    descripcion TEXT,
    CONSTRAINT chk_atencion CHECK (
        (estado_alerta = 'ACTIVA' AND atendida_por IS NULL AND fecha_atencion IS NULL)
        OR (estado_alerta IN ('ATENDIDA', 'RESUELTA'))
    ),
    CONSTRAINT chk_dias_umbral CHECK (dias_umbral IS NULL OR dias_umbral > 0)
);
