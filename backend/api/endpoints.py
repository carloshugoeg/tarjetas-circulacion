from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.core.database import get_db
from backend.crud import crud
from backend.models import models
from backend.schemas import schemas

router = APIRouter()


def commit_error_to_http(exc: IntegrityError):
    if "no puede tener mas de una tarjeta vigente" in str(exc.orig):
        raise HTTPException(status_code=409, detail="Un vehiculo no puede tener mas de una tarjeta activa (VIGENTE)")
    raise HTTPException(status_code=409, detail="Conflicto de integridad en la base de datos")


def validate_linea_marca(db: Session, marca_id: int, linea_id: int):
    if not crud.linea_belongs_to_marca(db, linea_id=linea_id, marca_id=marca_id):
        raise HTTPException(status_code=400, detail="La linea no pertenece a la marca seleccionada")


def validate_tarjeta_dates(current: models.TarjetaCirculacion, changes: schemas.TarjetaCirculacionUpdate):
    fecha_emision = changes.fecha_emision or current.fecha_emision
    fecha_vencimiento = changes.fecha_vencimiento or current.fecha_vencimiento
    if fecha_vencimiento <= fecha_emision:
        raise HTTPException(status_code=400, detail="fecha_vencimiento debe ser posterior a fecha_emision")


def validate_tarjetas_activas_limit(db: Session, vehiculo_id: int, exclude_tarjeta_id: int = None):
    vigentes = crud.count_tarjetas_vigentes_by_vehiculo(db, vehiculo_id, exclude_tarjeta_id)
    if vigentes >= crud.MAX_TARJETAS_VIGENTES_POR_VEHICULO:
        raise HTTPException(status_code=409, detail="Un vehiculo no puede tener mas de una tarjeta activa (VIGENTE)")


@router.get("/resumen/", tags=["Dashboard"])
def read_resumen(db: Session = Depends(get_db)):
    return crud.get_dashboard_summary(db)


# --- USUARIOS ---
@router.get("/usuarios/", response_model=List[schemas.UsuarioSistema], tags=["Usuarios"])
def read_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_usuarios(db, skip=skip, limit=limit)


@router.post("/usuarios/", response_model=schemas.UsuarioSistema, status_code=status.HTTP_201_CREATED, tags=["Usuarios"])
def create_usuario(usuario: schemas.UsuarioSistemaCreate, db: Session = Depends(get_db)):
    if crud.get_usuario_by_username(db, username=usuario.username):
        raise HTTPException(status_code=409, detail="Username already registered")
    try:
        return crud.create_usuario(db=db, usuario=usuario)
    except IntegrityError as exc:
        db.rollback()
        commit_error_to_http(exc)


# --- PROPIETARIOS ---
@router.get("/propietarios/", response_model=List[schemas.Propietario], tags=["Propietarios"])
def read_propietarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_propietarios(db, skip=skip, limit=limit)


@router.post("/propietarios/", response_model=schemas.Propietario, status_code=status.HTTP_201_CREATED, tags=["Propietarios"])
def create_propietario(propietario: schemas.PropietarioCreate, db: Session = Depends(get_db)):
    if crud.get_propietario_by_dpi(db, dpi=propietario.dpi):
        raise HTTPException(status_code=409, detail="DPI already registered")
    try:
        return crud.create_propietario(db=db, propietario=propietario)
    except IntegrityError as exc:
        db.rollback()
        commit_error_to_http(exc)


@router.patch("/propietarios/{propietario_id}", response_model=schemas.Propietario, tags=["Propietarios"])
def update_propietario(propietario_id: int, propietario: schemas.PropietarioUpdate, db: Session = Depends(get_db)):
    try:
        db_propietario = crud.update_propietario(db, propietario_id, propietario)
    except IntegrityError as exc:
        db.rollback()
        commit_error_to_http(exc)
    if not db_propietario:
        raise HTTPException(status_code=404, detail="Propietario not found")
    return db_propietario


@router.delete("/propietarios/{propietario_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Propietarios"])
def delete_propietario(propietario_id: int, db: Session = Depends(get_db)):
    try:
        db_propietario = crud.delete_propietario(db, propietario_id)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="No se puede eliminar: el propietario tiene tarjetas asociadas")
    if not db_propietario:
        raise HTTPException(status_code=404, detail="Propietario not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- VEHICULOS ---
@router.get("/vehiculos/", response_model=List[schemas.Vehiculo], tags=["Vehiculos"])
def read_vehiculos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_vehiculos(db, skip=skip, limit=limit)


@router.post("/vehiculos/", response_model=schemas.Vehiculo, status_code=status.HTTP_201_CREATED, tags=["Vehiculos"])
def create_vehiculo(vehiculo: schemas.VehiculoCreate, db: Session = Depends(get_db)):
    validate_linea_marca(db, vehiculo.id_marca, vehiculo.id_linea)
    if crud.get_vehiculo_by_vin(db, vin=vehiculo.vin):
        raise HTTPException(status_code=409, detail="VIN already registered")
    if crud.get_vehiculo_by_placa(db, placa=vehiculo.placa):
        raise HTTPException(status_code=409, detail="Placa already registered")
    try:
        return crud.create_vehiculo(db, vehiculo)
    except IntegrityError as exc:
        db.rollback()
        commit_error_to_http(exc)


@router.patch("/vehiculos/{vehiculo_id}", response_model=schemas.Vehiculo, tags=["Vehiculos"])
def update_vehiculo(vehiculo_id: int, vehiculo: schemas.VehiculoUpdate, db: Session = Depends(get_db)):
    db_vehiculo_actual = crud.get_vehiculo(db, vehiculo_id)
    if not db_vehiculo_actual:
        raise HTTPException(status_code=404, detail="Vehiculo not found")

    marca_id = vehiculo.id_marca if vehiculo.id_marca is not None else db_vehiculo_actual.id_marca
    linea_id = vehiculo.id_linea if vehiculo.id_linea is not None else db_vehiculo_actual.id_linea
    validate_linea_marca(db, marca_id, linea_id)

    try:
        return crud.update_vehiculo(db, vehiculo_id, vehiculo)
    except IntegrityError as exc:
        db.rollback()
        commit_error_to_http(exc)


@router.delete("/vehiculos/{vehiculo_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Vehiculos"])
def delete_vehiculo(vehiculo_id: int, db: Session = Depends(get_db)):
    try:
        db_vehiculo = crud.delete_vehiculo(db, vehiculo_id)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="No se puede eliminar: el vehiculo tiene tarjetas asociadas")
    if not db_vehiculo:
        raise HTTPException(status_code=404, detail="Vehiculo not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- TARJETAS ---
@router.get("/tarjetas/", response_model=List[schemas.TarjetaCirculacion], tags=["Tarjetas"])
def read_tarjetas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_tarjetas(db, skip=skip, limit=limit)


@router.get("/tarjetas/{tarjeta_id}", response_model=schemas.TarjetaCirculacion, tags=["Tarjetas"])
def read_tarjeta(tarjeta_id: int, db: Session = Depends(get_db)):
    db_tarjeta = crud.get_tarjeta(db, tarjeta_id=tarjeta_id)
    if db_tarjeta is None:
        raise HTTPException(status_code=404, detail="Tarjeta not found")
    return db_tarjeta


@router.post("/tarjetas/", response_model=schemas.TarjetaCirculacion, status_code=status.HTTP_201_CREATED, tags=["Tarjetas"])
def create_tarjeta(tarjeta: schemas.TarjetaCirculacionCreate, db: Session = Depends(get_db)):
    if crud.get_tarjeta_by_numero(db, tarjeta.numero_tarjeta):
        raise HTTPException(status_code=409, detail="Numero de tarjeta already registered")
    if tarjeta.estado == models.EstadoTarjetaEnum.VIGENTE:
        validate_tarjetas_activas_limit(db, tarjeta.id_vehiculo)
    try:
        return crud.create_tarjeta(db, tarjeta)
    except IntegrityError as exc:
        db.rollback()
        commit_error_to_http(exc)


@router.patch("/tarjetas/{tarjeta_id}", response_model=schemas.TarjetaCirculacion, tags=["Tarjetas"])
def update_tarjeta(tarjeta_id: int, tarjeta: schemas.TarjetaCirculacionUpdate, db: Session = Depends(get_db)):
    current = crud.get_tarjeta(db, tarjeta_id)
    if not current:
        raise HTTPException(status_code=404, detail="Tarjeta not found")
    validate_tarjeta_dates(current, tarjeta)
    next_vehiculo_id = tarjeta.id_vehiculo if tarjeta.id_vehiculo is not None else current.id_vehiculo
    next_estado = tarjeta.estado if tarjeta.estado is not None else current.estado
    if next_estado == models.EstadoTarjetaEnum.VIGENTE:
        validate_tarjetas_activas_limit(db, next_vehiculo_id, exclude_tarjeta_id=tarjeta_id)

    try:
        db_tarjeta = crud.update_tarjeta(db, tarjeta_id, tarjeta)
    except IntegrityError as exc:
        db.rollback()
        commit_error_to_http(exc)
    return db_tarjeta


@router.delete("/tarjetas/{tarjeta_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tarjetas"])
def delete_tarjeta(tarjeta_id: int, db: Session = Depends(get_db)):
    try:
        db_tarjeta = crud.delete_tarjeta(db, tarjeta_id)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="No se puede eliminar: la tarjeta tiene historial o alertas asociadas")
    if not db_tarjeta:
        raise HTTPException(status_code=404, detail="Tarjeta not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- MANTENIMIENTO ---
@router.patch("/tarjetas/{tarjeta_id}/cambio-propietario", response_model=schemas.TarjetaCirculacion, tags=["Mantenimiento"])
def update_propietario_tarjeta(tarjeta_id: int, payload: schemas.CambioPropietarioRequest, db: Session = Depends(get_db)):
    tarjeta_actual = crud.get_tarjeta(db, tarjeta_id)
    if not tarjeta_actual:
        raise HTTPException(status_code=404, detail="Tarjeta not found")
    if not crud.get_propietario(db, payload.nuevo_propietario_id):
        raise HTTPException(status_code=404, detail="Nuevo propietario not found")
    if tarjeta_actual.id_propietario == payload.nuevo_propietario_id:
        raise HTTPException(status_code=400, detail="El nuevo propietario debe ser diferente al propietario actual")
    return crud.update_propietario_tarjeta(db, tarjeta_id, payload.nuevo_propietario_id, payload.usuario_id)


@router.patch("/vehiculos/{vehiculo_id}/cambio-motor", response_model=schemas.Vehiculo, tags=["Mantenimiento"])
def update_motor(vehiculo_id: int, payload: schemas.CambioMotorRequest, db: Session = Depends(get_db)):
    vehiculo_actual = crud.get_vehiculo(db, vehiculo_id)
    if not vehiculo_actual:
        raise HTTPException(status_code=404, detail="Vehiculo not found")
    if vehiculo_actual.numero_motor == payload.nuevo_motor:
        raise HTTPException(status_code=400, detail="El nuevo motor debe ser diferente al motor actual")
    return crud.update_motor_vehiculo(db, vehiculo_id, payload.nuevo_motor, payload.usuario_id)


@router.patch("/vehiculos/{vehiculo_id}/cambio-color", response_model=schemas.Vehiculo, tags=["Mantenimiento"])
def update_color(vehiculo_id: int, payload: schemas.CambioColorRequest, db: Session = Depends(get_db)):
    vehiculo_actual = crud.get_vehiculo(db, vehiculo_id)
    if not vehiculo_actual:
        raise HTTPException(status_code=404, detail="Vehiculo not found")
    if not db.get(models.Color, payload.nuevo_color_id):
        raise HTTPException(status_code=404, detail="Color not found")
    if vehiculo_actual.id_color == payload.nuevo_color_id:
        raise HTTPException(status_code=400, detail="El nuevo color debe ser diferente al color actual")
    return crud.update_color_vehiculo(db, vehiculo_id, payload.nuevo_color_id, payload.usuario_id)


@router.patch("/tarjetas/{tarjeta_id}/desactivar", response_model=schemas.TarjetaCirculacion, tags=["Mantenimiento"])
def deactivate_tarjeta(tarjeta_id: int, payload: schemas.DesactivarTarjetaRequest, db: Session = Depends(get_db)):
    tarjeta_actual = crud.get_tarjeta(db, tarjeta_id)
    if not tarjeta_actual:
        raise HTTPException(status_code=404, detail="Tarjeta not found")
    if payload.nuevo_estado == models.EstadoTarjetaEnum.VIGENTE:
        raise HTTPException(status_code=400, detail="Usa reactivar para volver a estado VIGENTE")
    if tarjeta_actual.estado == payload.nuevo_estado:
        raise HTTPException(status_code=400, detail="El nuevo estado debe ser diferente al estado actual")
    return crud.deactivate_tarjeta(db, tarjeta_id, payload.nuevo_estado, payload.motivo, payload.usuario_id)


@router.patch("/tarjetas/{tarjeta_id}/reactivar", response_model=schemas.TarjetaCirculacion, tags=["Mantenimiento"])
def reactivate_tarjeta(tarjeta_id: int, payload: schemas.ReactivarTarjetaRequest, db: Session = Depends(get_db)):
    tarjeta_actual = crud.get_tarjeta(db, tarjeta_id)
    if not tarjeta_actual:
        raise HTTPException(status_code=404, detail="Tarjeta not found")
    if tarjeta_actual.estado == models.EstadoTarjetaEnum.VIGENTE:
        raise HTTPException(status_code=400, detail="La tarjeta ya esta vigente")
    validate_tarjetas_activas_limit(db, tarjeta_actual.id_vehiculo, exclude_tarjeta_id=tarjeta_id)
    return crud.reactivate_tarjeta(db, tarjeta_id, payload.motivo, payload.usuario_id)


# --- CATALOGOS ---
@router.get("/catalogos/departamentos/", response_model=List[schemas.Departamento], tags=["Catalogos"])
def read_departamentos(db: Session = Depends(get_db)):
    return crud.get_departamentos(db)


@router.get("/catalogos/municipios/", response_model=List[schemas.Municipio], tags=["Catalogos"])
def read_municipios(departamento_id: Optional[int] = None, db: Session = Depends(get_db)):
    return crud.get_municipios(db, departamento_id=departamento_id)


@router.get("/catalogos/tipos-vehiculo/", response_model=List[schemas.TipoVehiculo], tags=["Catalogos"])
def read_tipos_vehiculo(db: Session = Depends(get_db)):
    return crud.get_tipos_vehiculo(db)


@router.get("/catalogos/marcas/", response_model=List[schemas.MarcaVehiculo], tags=["Catalogos"])
def read_marcas(db: Session = Depends(get_db)):
    return crud.get_marcas_vehiculo(db)


@router.get("/catalogos/lineas/", response_model=List[schemas.LineaVehiculo], tags=["Catalogos"])
def read_lineas(marca_id: Optional[int] = None, db: Session = Depends(get_db)):
    return crud.get_lineas_vehiculo(db, marca_id=marca_id)


@router.get("/catalogos/colores/", response_model=List[schemas.Color], tags=["Catalogos"])
def read_colores(db: Session = Depends(get_db)):
    return crud.get_colores(db)


@router.get("/historial/", response_model=List[schemas.HistorialCambios], tags=["Auditoria"])
def read_historial(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_historial(db, skip=skip, limit=limit)


@router.get("/alertas/", response_model=List[schemas.Alerta], tags=["Auditoria"])
def read_alertas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_alertas(db, skip=skip, limit=limit)
