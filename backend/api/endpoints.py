from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from backend.crud import crud
from backend.schemas import schemas
from backend.models import models
from backend.core.database import get_db

router = APIRouter()


def commit_error_to_http(exc: IntegrityError):
    detail = str(exc.orig) if getattr(exc, "orig", None) else "No se pudo completar la operacion"
    raise HTTPException(status_code=400, detail=detail)


@router.get("/resumen/", tags=["Dashboard"])
def read_resumen(db: Session = Depends(get_db)):
    return crud.get_dashboard_summary(db)

# --- USUARIOS ---
@router.get("/usuarios/", response_model=List[schemas.UsuarioSistema], tags=["Usuarios"])
def read_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    usuarios = crud.get_usuarios(db, skip=skip, limit=limit)
    return usuarios

@router.post("/usuarios/", response_model=schemas.UsuarioSistema, tags=["Usuarios"])
def create_usuario(usuario: schemas.UsuarioSistemaCreate, db: Session = Depends(get_db)):
    db_usuario = crud.get_usuario_by_username(db, username=usuario.username)
    if db_usuario:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_usuario(db=db, usuario=usuario)

# --- PROPIETARIOS ---
@router.get("/propietarios/", response_model=List[schemas.Propietario], tags=["Propietarios"])
def read_propietarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    propietarios = crud.get_propietarios(db, skip=skip, limit=limit)
    return propietarios

@router.post("/propietarios/", response_model=schemas.Propietario, tags=["Propietarios"])
def create_propietario(propietario: schemas.PropietarioCreate, db: Session = Depends(get_db)):
    db_propietario = crud.get_propietario_by_dpi(db, dpi=propietario.dpi)
    if db_propietario:
        raise HTTPException(status_code=400, detail="DPI already registered")
    return crud.create_propietario(db=db, propietario=propietario)

@router.put("/propietarios/{propietario_id}", response_model=schemas.Propietario, tags=["Propietarios"])
def update_propietario(propietario_id: int, propietario: schemas.PropietarioUpdate, db: Session = Depends(get_db)):
    try:
        db_propietario = crud.update_propietario(db, propietario_id, propietario)
    except IntegrityError as exc:
        db.rollback()
        commit_error_to_http(exc)
    if not db_propietario:
        raise HTTPException(status_code=404, detail="Propietario not found")
    return db_propietario

@router.delete("/propietarios/{propietario_id}", tags=["Propietarios"])
def delete_propietario(propietario_id: int, db: Session = Depends(get_db)):
    try:
        db_propietario = crud.delete_propietario(db, propietario_id)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="No se puede eliminar: el propietario tiene tarjetas asociadas")
    if not db_propietario:
        raise HTTPException(status_code=404, detail="Propietario not found")
    return {"ok": True}

# --- VEHICULOS ---
@router.get("/vehiculos/", response_model=List[schemas.Vehiculo], tags=["Vehiculos"])
def read_vehiculos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_vehiculos(db, skip=skip, limit=limit)

@router.post("/vehiculos/", response_model=schemas.Vehiculo, tags=["Vehiculos"])
def create_vehiculo(vehiculo: schemas.VehiculoCreate, db: Session = Depends(get_db)):
    db_v = crud.get_vehiculo_by_vin(db, vin=vehiculo.vin)
    if db_v:
        raise HTTPException(status_code=400, detail="VIN already registered")
    db_p = crud.get_vehiculo_by_placa(db, placa=vehiculo.placa)
    if db_p:
        raise HTTPException(status_code=400, detail="Placa already registered")
    return crud.create_vehiculo(db, vehiculo)

@router.put("/vehiculos/{vehiculo_id}", response_model=schemas.Vehiculo, tags=["Vehiculos"])
def update_vehiculo(vehiculo_id: int, vehiculo: schemas.VehiculoUpdate, db: Session = Depends(get_db)):
    try:
        db_vehiculo = crud.update_vehiculo(db, vehiculo_id, vehiculo)
    except IntegrityError as exc:
        db.rollback()
        commit_error_to_http(exc)
    if not db_vehiculo:
        raise HTTPException(status_code=404, detail="Vehiculo not found")
    return db_vehiculo

@router.delete("/vehiculos/{vehiculo_id}", tags=["Vehiculos"])
def delete_vehiculo(vehiculo_id: int, db: Session = Depends(get_db)):
    try:
        db_vehiculo = crud.delete_vehiculo(db, vehiculo_id)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="No se puede eliminar: el vehiculo tiene tarjetas asociadas")
    if not db_vehiculo:
        raise HTTPException(status_code=404, detail="Vehiculo not found")
    return {"ok": True}

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

@router.post("/tarjetas/", response_model=schemas.TarjetaCirculacion, tags=["Tarjetas"])
def create_tarjeta(tarjeta: schemas.TarjetaCirculacionCreate, db: Session = Depends(get_db)):
    return crud.create_tarjeta(db, tarjeta)

@router.put("/tarjetas/{tarjeta_id}", response_model=schemas.TarjetaCirculacion, tags=["Tarjetas"])
def update_tarjeta(tarjeta_id: int, tarjeta: schemas.TarjetaCirculacionUpdate, db: Session = Depends(get_db)):
    try:
        db_tarjeta = crud.update_tarjeta(db, tarjeta_id, tarjeta)
    except IntegrityError as exc:
        db.rollback()
        commit_error_to_http(exc)
    if not db_tarjeta:
        raise HTTPException(status_code=404, detail="Tarjeta not found")
    return db_tarjeta

@router.delete("/tarjetas/{tarjeta_id}", tags=["Tarjetas"])
def delete_tarjeta(tarjeta_id: int, db: Session = Depends(get_db)):
    try:
        db_tarjeta = crud.delete_tarjeta(db, tarjeta_id)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="No se puede eliminar: la tarjeta tiene historial o alertas asociadas")
    if not db_tarjeta:
        raise HTTPException(status_code=404, detail="Tarjeta not found")
    return {"ok": True}

# --- MANTENIMIENTO ---
@router.put("/tarjetas/{tarjeta_id}/cambio-propietario", response_model=schemas.TarjetaCirculacion, tags=["Mantenimiento"])
def update_propietario(tarjeta_id: int, nuevo_propietario_id: int, usuario_id: Optional[int] = None, db: Session = Depends(get_db)):
    tarjeta_actual = crud.get_tarjeta(db, tarjeta_id)
    if not tarjeta_actual:
        raise HTTPException(status_code=404, detail="Tarjeta not found")
    if tarjeta_actual.id_propietario == nuevo_propietario_id:
        raise HTTPException(status_code=400, detail="El nuevo propietario debe ser diferente al propietario actual")
    db_tarjeta = crud.update_propietario_tarjeta(db, tarjeta_id, nuevo_propietario_id, usuario_id)
    return db_tarjeta

@router.put("/vehiculos/{vehiculo_id}/cambio-motor", response_model=schemas.Vehiculo, tags=["Mantenimiento"])
def update_motor(vehiculo_id: int, nuevo_motor: str, usuario_id: Optional[int] = None, db: Session = Depends(get_db)):
    vehiculo_actual = crud.get_vehiculo(db, vehiculo_id)
    if not vehiculo_actual:
        raise HTTPException(status_code=404, detail="Vehiculo not found")
    if vehiculo_actual.numero_motor == nuevo_motor:
        raise HTTPException(status_code=400, detail="El nuevo motor debe ser diferente al motor actual")
    db_vehiculo = crud.update_motor_vehiculo(db, vehiculo_id, nuevo_motor, usuario_id)
    return db_vehiculo

@router.put("/vehiculos/{vehiculo_id}/cambio-color", response_model=schemas.Vehiculo, tags=["Mantenimiento"])
def update_color(vehiculo_id: int, nuevo_color_id: int, usuario_id: Optional[int] = None, db: Session = Depends(get_db)):
    vehiculo_actual = crud.get_vehiculo(db, vehiculo_id)
    if not vehiculo_actual:
        raise HTTPException(status_code=404, detail="Vehiculo not found")
    if vehiculo_actual.id_color == nuevo_color_id:
        raise HTTPException(status_code=400, detail="El nuevo color debe ser diferente al color actual")
    db_vehiculo = crud.update_color_vehiculo(db, vehiculo_id, nuevo_color_id, usuario_id)
    return db_vehiculo

@router.put("/tarjetas/{tarjeta_id}/desactivar", response_model=schemas.TarjetaCirculacion, tags=["Mantenimiento"])
def deactivate_tarjeta(tarjeta_id: int, nuevo_estado: models.EstadoTarjetaEnum, motivo: Optional[str] = None, usuario_id: Optional[int] = None, db: Session = Depends(get_db)):
    tarjeta_actual = crud.get_tarjeta(db, tarjeta_id)
    if not tarjeta_actual:
        raise HTTPException(status_code=404, detail="Tarjeta not found")
    if tarjeta_actual.estado == nuevo_estado:
        raise HTTPException(status_code=400, detail="El nuevo estado debe ser diferente al estado actual")
    db_tarjeta = crud.deactivate_tarjeta(db, tarjeta_id, nuevo_estado, motivo, usuario_id)
    return db_tarjeta

@router.put("/tarjetas/{tarjeta_id}/reactivar", response_model=schemas.TarjetaCirculacion, tags=["Mantenimiento"])
def reactivate_tarjeta(tarjeta_id: int, motivo: Optional[str] = None, usuario_id: Optional[int] = None, db: Session = Depends(get_db)):
    tarjeta_actual = crud.get_tarjeta(db, tarjeta_id)
    if not tarjeta_actual:
        raise HTTPException(status_code=404, detail="Tarjeta not found")
    if tarjeta_actual.estado == models.EstadoTarjetaEnum.VIGENTE:
        raise HTTPException(status_code=400, detail="La tarjeta ya esta vigente")
    db_tarjeta = crud.reactivate_tarjeta(db, tarjeta_id, motivo, usuario_id)
    return db_tarjeta

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
