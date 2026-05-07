from sqlalchemy.orm import Session
from backend.models import models
from backend.schemas import schemas
from datetime import datetime, date, timedelta


def apply_updates(db_obj, values: dict):
    for key, value in values.items():
        setattr(db_obj, key, value)
    return db_obj

# --- USUARIO_SISTEMA ---
def get_usuario(db: Session, usuario_id: int):
    return db.query(models.UsuarioSistema).filter(models.UsuarioSistema.id_usuario == usuario_id).first()

def get_usuario_by_username(db: Session, username: str):
    return db.query(models.UsuarioSistema).filter(models.UsuarioSistema.username == username).first()

def get_usuarios(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.UsuarioSistema).offset(skip).limit(limit).all()

def create_usuario(db: Session, usuario: schemas.UsuarioSistemaCreate):
    db_usuario = models.UsuarioSistema(**usuario.model_dump())
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

# --- PROPIETARIO ---
def get_propietario(db: Session, propietario_id: int):
    return db.query(models.Propietario).filter(models.Propietario.id_propietario == propietario_id).first()

def get_propietario_by_dpi(db: Session, dpi: str):
    return db.query(models.Propietario).filter(models.Propietario.dpi == dpi).first()

def get_propietarios(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Propietario).offset(skip).limit(limit).all()

def create_propietario(db: Session, propietario: schemas.PropietarioCreate):
    db_propietario = models.Propietario(**propietario.model_dump())
    db.add(db_propietario)
    db.commit()
    db.refresh(db_propietario)
    return db_propietario

def update_propietario(db: Session, propietario_id: int, propietario: schemas.PropietarioUpdate):
    db_propietario = get_propietario(db, propietario_id)
    if not db_propietario:
        return None
    apply_updates(db_propietario, propietario.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(db_propietario)
    return db_propietario

def delete_propietario(db: Session, propietario_id: int):
    db_propietario = get_propietario(db, propietario_id)
    if not db_propietario:
        return None
    db.delete(db_propietario)
    db.commit()
    return db_propietario

# --- VEHICULO ---
def get_vehiculo(db: Session, vehiculo_id: int):
    return db.query(models.Vehiculo).filter(models.Vehiculo.id_vehiculo == vehiculo_id).first()

def get_vehiculo_by_vin(db: Session, vin: str):
    return db.query(models.Vehiculo).filter(models.Vehiculo.vin == vin).first()

def get_vehiculo_by_placa(db: Session, placa: str):
    return db.query(models.Vehiculo).filter(models.Vehiculo.placa == placa).first()

def linea_belongs_to_marca(db: Session, linea_id: int, marca_id: int):
    return db.query(models.LineaVehiculo).filter(
        models.LineaVehiculo.id_linea == linea_id,
        models.LineaVehiculo.id_marca == marca_id,
    ).first() is not None

def get_vehiculos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Vehiculo).offset(skip).limit(limit).all()

def create_vehiculo(db: Session, vehiculo: schemas.VehiculoCreate):
    db_vehiculo = models.Vehiculo(**vehiculo.model_dump())
    db.add(db_vehiculo)
    db.commit()
    db.refresh(db_vehiculo)
    return db_vehiculo

def update_vehiculo(db: Session, vehiculo_id: int, vehiculo: schemas.VehiculoUpdate):
    db_vehiculo = get_vehiculo(db, vehiculo_id)
    if not db_vehiculo:
        return None
    apply_updates(db_vehiculo, vehiculo.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(db_vehiculo)
    return db_vehiculo

def delete_vehiculo(db: Session, vehiculo_id: int):
    db_vehiculo = get_vehiculo(db, vehiculo_id)
    if not db_vehiculo:
        return None
    db.delete(db_vehiculo)
    db.commit()
    return db_vehiculo

# --- TARJETA_CIRCULACION ---
def get_tarjeta(db: Session, tarjeta_id: int):
    return db.query(models.TarjetaCirculacion).filter(models.TarjetaCirculacion.id_tarjeta == tarjeta_id).first()

def get_tarjeta_by_numero(db: Session, numero_tarjeta: str):
    return db.query(models.TarjetaCirculacion).filter(models.TarjetaCirculacion.numero_tarjeta == numero_tarjeta).first()

def get_tarjetas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.TarjetaCirculacion).offset(skip).limit(limit).all()

def create_tarjeta(db: Session, tarjeta: schemas.TarjetaCirculacionCreate):
    db_tarjeta = models.TarjetaCirculacion(**tarjeta.model_dump())
    db.add(db_tarjeta)
    db.commit()
    db.refresh(db_tarjeta)
    return db_tarjeta

def update_tarjeta(db: Session, tarjeta_id: int, tarjeta: schemas.TarjetaCirculacionUpdate):
    db_tarjeta = get_tarjeta(db, tarjeta_id)
    if not db_tarjeta:
        return None
    apply_updates(db_tarjeta, tarjeta.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(db_tarjeta)
    return db_tarjeta

def delete_tarjeta(db: Session, tarjeta_id: int):
    db_tarjeta = get_tarjeta(db, tarjeta_id)
    if not db_tarjeta:
        return None
    db.delete(db_tarjeta)
    db.commit()
    return db_tarjeta

def get_historial(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.HistorialCambios).order_by(models.HistorialCambios.fecha_hora.desc()).offset(skip).limit(limit).all()

def get_alertas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Alerta).order_by(models.Alerta.fecha_generacion.desc()).offset(skip).limit(limit).all()

def get_dashboard_summary(db: Session):
    total_tarjetas = db.query(models.TarjetaCirculacion).count()
    vigentes = db.query(models.TarjetaCirculacion).filter(models.TarjetaCirculacion.estado == models.EstadoTarjetaEnum.VIGENTE).count()
    suspendidas = db.query(models.TarjetaCirculacion).filter(models.TarjetaCirculacion.estado == models.EstadoTarjetaEnum.SUSPENDIDA).count()
    vencidas = db.query(models.TarjetaCirculacion).filter(models.TarjetaCirculacion.fecha_vencimiento < date.today()).count()
    proximas = db.query(models.TarjetaCirculacion).filter(
        models.TarjetaCirculacion.fecha_vencimiento >= date.today(),
        models.TarjetaCirculacion.fecha_vencimiento <= date.today() + timedelta(days=30),
    ).count()
    return {
        "total_tarjetas": total_tarjetas,
        "vigentes": vigentes,
        "suspendidas": suspendidas,
        "vencidas": vencidas,
        "vencen_pronto": proximas,
        "propietarios": db.query(models.Propietario).count(),
        "vehiculos": db.query(models.Vehiculo).count(),
        "alertas_activas": db.query(models.Alerta).filter(models.Alerta.estado_alerta == models.EstadoAlertaEnum.ACTIVA).count(),
    }

# --- MANTENIMIENTO & AUDITORIA ---
def log_cambio(db: Session, tarjeta_id: int, tipo: models.TipoCambioEnum, anterior: str, nuevo: str, usuario_id: int = None):
    db_historial = models.HistorialCambios(
        id_tarjeta=tarjeta_id,
        tipo_cambio=tipo,
        valor_anterior=anterior,
        valor_nuevo=nuevo,
        usuario_responsable=usuario_id
    )
    db.add(db_historial)

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

def update_motor_vehiculo(db: Session, vehiculo_id: int, nuevo_motor: str, usuario_id: int = None):
    db_vehiculo = get_vehiculo(db, vehiculo_id)
    if not db_vehiculo:
        return None
    
    valor_anterior = db_vehiculo.numero_motor
    db_vehiculo.numero_motor = nuevo_motor
    
    # Buscamos la tarjeta vigente para registrar el cambio
    db_tarjeta = db.query(models.TarjetaCirculacion).filter(
        models.TarjetaCirculacion.id_vehiculo == vehiculo_id,
        models.TarjetaCirculacion.estado == models.EstadoTarjetaEnum.VIGENTE
    ).first()
    
    if db_tarjeta:
        log_cambio(db, db_tarjeta.id_tarjeta, models.TipoCambioEnum.MOTOR, valor_anterior, nuevo_motor, usuario_id)
    
    db.commit()
    db.refresh(db_vehiculo)
    return db_vehiculo

def update_color_vehiculo(db: Session, vehiculo_id: int, nuevo_color_id: int, usuario_id: int = None):
    db_vehiculo = get_vehiculo(db, vehiculo_id)
    if not db_vehiculo:
        return None

    valor_anterior = str(db_vehiculo.id_color)
    db_vehiculo.id_color = nuevo_color_id

    db_tarjeta = db.query(models.TarjetaCirculacion).filter(
        models.TarjetaCirculacion.id_vehiculo == vehiculo_id,
        models.TarjetaCirculacion.estado == models.EstadoTarjetaEnum.VIGENTE
    ).first()

    if db_tarjeta:
        log_cambio(db, db_tarjeta.id_tarjeta, models.TipoCambioEnum.COLOR, valor_anterior, str(nuevo_color_id), usuario_id)

    db.commit()
    db.refresh(db_vehiculo)
    return db_vehiculo

def deactivate_tarjeta(db: Session, tarjeta_id: int, nuevo_estado: models.EstadoTarjetaEnum, motivo: str = None, usuario_id: int = None):
    db_tarjeta = get_tarjeta(db, tarjeta_id)
    if not db_tarjeta:
        return None
    
    valor_anterior = db_tarjeta.estado.value
    db_tarjeta.estado = nuevo_estado
    if motivo:
        db_tarjeta.observaciones = (db_tarjeta.observaciones or "") + f"\nMotivo desactivación: {motivo}"
    
    log_cambio(db, tarjeta_id, models.TipoCambioEnum.ESTADO, valor_anterior, nuevo_estado.value, usuario_id)
    
    # Si es impago o suspensión, generar alerta
    if nuevo_estado in [models.EstadoTarjetaEnum.SUSPENDIDA, models.EstadoTarjetaEnum.CANCELADA]:
        tipo_alerta = models.TipoAlertaEnum.SUSPENSION_ADMINISTRATIVA
        if "impago" in (motivo or "").lower():
            tipo_alerta = models.TipoAlertaEnum.IMPAGO
            
        db_alerta = models.Alerta(
            id_tarjeta=tarjeta_id,
            tipo_alerta=tipo_alerta,
            descripcion=motivo
        )
        db.add(db_alerta)
    
    db.commit()
    db.refresh(db_tarjeta)
    return db_tarjeta

def reactivate_tarjeta(db: Session, tarjeta_id: int, motivo: str = None, usuario_id: int = None):
    db_tarjeta = get_tarjeta(db, tarjeta_id)
    if not db_tarjeta:
        return None

    valor_anterior = db_tarjeta.estado.value
    db_tarjeta.estado = models.EstadoTarjetaEnum.VIGENTE
    if motivo:
        db_tarjeta.observaciones = (db_tarjeta.observaciones or "") + f"\nMotivo reactivacion: {motivo}"

    log_cambio(db, tarjeta_id, models.TipoCambioEnum.ESTADO, valor_anterior, models.EstadoTarjetaEnum.VIGENTE.value, usuario_id)

    alertas_activas = db.query(models.Alerta).filter(
        models.Alerta.id_tarjeta == tarjeta_id,
        models.Alerta.estado_alerta == models.EstadoAlertaEnum.ACTIVA
    ).all()

    for alerta in alertas_activas:
        alerta.estado_alerta = models.EstadoAlertaEnum.RESUELTA
        alerta.fecha_atencion = datetime.now()
        alerta.atendida_por = usuario_id
        if motivo:
            alerta.descripcion = (alerta.descripcion or "") + f"\nReactivacion: {motivo}"

    db.commit()
    db.refresh(db_tarjeta)
    return db_tarjeta

# --- CATALOGS ---
def get_departamentos(db: Session):
    return db.query(models.Departamento).all()

def get_municipios(db: Session, departamento_id: int = None):
    query = db.query(models.Municipio)
    if departamento_id:
        query = query.filter(models.Municipio.id_departamento == departamento_id)
    return query.all()

def get_tipos_vehiculo(db: Session):
    return db.query(models.TipoVehiculo).all()

def get_marcas_vehiculo(db: Session):
    return db.query(models.MarcaVehiculo).all()

def get_lineas_vehiculo(db: Session, marca_id: int = None):
    query = db.query(models.LineaVehiculo)
    if marca_id:
        query = query.filter(models.LineaVehiculo.id_marca == marca_id)
    return query.all()

def get_colores(db: Session):
    return db.query(models.Color).all()
