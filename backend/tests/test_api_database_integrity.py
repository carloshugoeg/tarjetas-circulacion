import os
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    pytest.skip("Set TEST_DATABASE_URL to run PostgreSQL integration tests.", allow_module_level=True)

os.environ.setdefault("DATABASE_URL", TEST_DATABASE_URL)

from backend.core.database import Base, get_db
from backend.main import app
from backend.models import models

@pytest.fixture()
def db_session():
    engine = create_engine(TEST_DATABASE_URL)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    seed_reference_data(db)
    db.close()

    try:
        yield TestingSessionLocal
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        db = db_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def seed_reference_data(db):
    departamento = models.Departamento(nombre="Guatemala", codigo="01")
    tipo = models.TipoVehiculo(nombre="Automovil", descripcion="Vehiculo liviano")
    color_rojo = models.Color(nombre="Rojo")
    color_azul = models.Color(nombre="Azul")
    marca_toyota = models.MarcaVehiculo(nombre="Toyota")
    marca_honda = models.MarcaVehiculo(nombre="Honda")
    usuario = models.UsuarioSistema(username="admin", nombre_completo="Admin Test")
    db.add_all([departamento, tipo, color_rojo, color_azul, marca_toyota, marca_honda, usuario])
    db.flush()

    municipio = models.Municipio(id_departamento=departamento.id_departamento, nombre="Guatemala")
    linea_corolla = models.LineaVehiculo(id_marca=marca_toyota.id_marca, nombre="Corolla")
    linea_civic = models.LineaVehiculo(id_marca=marca_honda.id_marca, nombre="Civic")
    db.add_all([municipio, linea_corolla, linea_civic])
    db.flush()

    propietario_1 = models.Propietario(
        dpi="1234567890101",
        primer_nombre="Ana",
        primer_apellido="Lopez",
        fecha_nacimiento=date(1990, 1, 1),
        direccion="Zona 1",
        id_municipio=municipio.id_municipio,
        telefono="12345678",
        correo="ana@example.com",
    )
    propietario_2 = models.Propietario(
        dpi="1234567890102",
        primer_nombre="Luis",
        primer_apellido="Perez",
        fecha_nacimiento=date(1988, 5, 20),
        direccion="Zona 2",
        id_municipio=municipio.id_municipio,
        telefono="22223333",
    )
    propietario_sin_tarjeta = models.Propietario(
        dpi="1234567890103",
        primer_nombre="Marta",
        primer_apellido="Diaz",
        fecha_nacimiento=date(1995, 7, 15),
        direccion="Zona 3",
        id_municipio=municipio.id_municipio,
        telefono="44445555",
    )
    db.add_all([propietario_1, propietario_2, propietario_sin_tarjeta])
    db.flush()

    vehiculo = models.Vehiculo(
        vin="1HGCM82633A004352",
        placa="P123ABC",
        id_tipo_vehiculo=tipo.id_tipo_vehiculo,
        id_marca=marca_toyota.id_marca,
        id_linea=linea_corolla.id_linea,
        modelo_anio=2022,
        id_color=color_rojo.id_color,
        numero_motor="MOTOR-1",
        numero_chasis="CHASIS-1",
        ejes=2,
        combustible=models.TipoCombustibleEnum.GASOLINA,
        uso=models.UsoVehiculoEnum.PARTICULAR,
    )
    db.add(vehiculo)
    db.flush()

    tarjeta = models.TarjetaCirculacion(
        id_vehiculo=vehiculo.id_vehiculo,
        id_propietario=propietario_1.id_propietario,
        numero_tarjeta="TC-BASE-000001",
        fecha_emision=date.today(),
        fecha_vencimiento=date.today() + timedelta(days=365),
        estado=models.EstadoTarjetaEnum.VIGENTE,
        id_usuario_emision=usuario.id_usuario,
    )
    db.add(tarjeta)
    db.commit()


def test_partial_resource_updates_use_patch_and_preserve_unspecified_fields(client):
    response = client.patch("/api/propietarios/1", json={"telefono": "87654321"})

    assert response.status_code == 200
    body = response.json()
    assert body["telefono"] == "87654321"
    assert body["primer_nombre"] == "Ana"
    assert body["direccion"] == "Zona 1"

    put_response = client.put("/api/propietarios/1", json={"telefono": "11112222"})
    assert put_response.status_code == 405


def test_delete_returns_204_with_empty_body(client):
    response = client.delete("/api/propietarios/3")

    assert response.status_code == 204
    assert response.content == b""

    remaining_ids = {item["id_propietario"] for item in client.get("/api/propietarios/").json()}
    assert 3 not in remaining_ids


def test_maintenance_transitions_use_patch_json_body_and_write_audit(client):
    response = client.patch(
        "/api/vehiculos/1/cambio-motor",
        json={"nuevo_motor": "MOTOR-2", "usuario_id": 1},
    )

    assert response.status_code == 200
    assert response.json()["numero_motor"] == "MOTOR-2"

    historial = client.get("/api/historial/").json()
    assert any(
        item["tipo_cambio"] == "MOTOR"
        and item["valor_anterior"] == "MOTOR-1"
        and item["valor_nuevo"] == "MOTOR-2"
        for item in historial
    )


def test_duplicate_tarjeta_returns_conflict_and_session_recovers(client):
    duplicate_payload = tarjeta_payload(numero_tarjeta="TC-BASE-000001")
    duplicate = client.post("/api/tarjetas/", json=duplicate_payload)

    assert duplicate.status_code == 409

    valid = client.post("/api/tarjetas/", json=tarjeta_payload(numero_tarjeta="TC-BASE-000002", estado="SUSPENDIDA"))
    assert valid.status_code == 201
    assert valid.json()["numero_tarjeta"] == "TC-BASE-000002"


def test_vehicle_cannot_have_more_than_one_active_card(client):
    second = client.post("/api/tarjetas/", json=tarjeta_payload(numero_tarjeta="TC-BASE-000002"))

    assert second.status_code == 409
    assert "mas de una tarjeta activa" in second.json()["detail"]


def test_vehicle_can_have_extra_inactive_cards(client):
    inactive = client.post(
        "/api/tarjetas/",
        json=tarjeta_payload(numero_tarjeta="TC-BASE-000002", estado="SUSPENDIDA"),
    )

    assert inactive.status_code == 201
    assert inactive.json()["estado"] == "SUSPENDIDA"


def test_tarjeta_update_cannot_exceed_active_card_limit(client):
    inactive = client.post(
        "/api/tarjetas/",
        json=tarjeta_payload(numero_tarjeta="TC-BASE-000002", estado="SUSPENDIDA"),
    )
    assert inactive.status_code == 201

    response = client.patch(f"/api/tarjetas/{inactive.json()['id_tarjeta']}", json={"estado": "VIGENTE"})

    assert response.status_code == 409
    assert "mas de una tarjeta activa" in response.json()["detail"]


def test_reactivate_tarjeta_cannot_exceed_active_card_limit(client):
    inactive = client.post(
        "/api/tarjetas/",
        json=tarjeta_payload(numero_tarjeta="TC-BASE-000002", estado="SUSPENDIDA"),
    )
    assert inactive.status_code == 201

    response = client.patch(
        f"/api/tarjetas/{inactive.json()['id_tarjeta']}/reactivar",
        json={"motivo": "Reactivacion de prueba"},
    )

    assert response.status_code == 409
    assert "mas de una tarjeta activa" in response.json()["detail"]


def test_database_trigger_blocks_more_than_one_active_card(db_session):
    db = db_session()
    try:
        db.add(
            models.TarjetaCirculacion(
                id_vehiculo=1,
                id_propietario=1,
                numero_tarjeta="TC-BASE-000002",
                fecha_emision=date.today(),
                fecha_vencimiento=date.today() + timedelta(days=365),
                estado=models.EstadoTarjetaEnum.VIGENTE,
                id_usuario_emision=1,
            )
        )

        with pytest.raises(IntegrityError):
            db.commit()
    finally:
        db.rollback()
        db.close()


def test_vehicle_line_must_belong_to_selected_brand(client):
    payload = vehiculo_payload(vin="1HGCM82633A004353", placa="P124ABC", id_marca=1, id_linea=2)
    response = client.post("/api/vehiculos/", json=payload)

    assert response.status_code == 400
    assert "linea" in response.json()["detail"].lower()


def test_vehicle_year_is_validated_before_database_commit(client):
    payload = vehiculo_payload(vin="1HGCM82633A004354", placa="P125ABC", modelo_anio=date.today().year + 2)
    response = client.post("/api/vehiculos/", json=payload)

    assert response.status_code == 422


def test_tarjeta_requires_expiration_after_issue_date(client):
    payload = tarjeta_payload(
        numero_tarjeta="TC-BASE-000003",
        fecha_emision="2026-01-10",
        fecha_vencimiento="2026-01-10",
    )
    response = client.post("/api/tarjetas/", json=payload)

    assert response.status_code == 422


def test_partial_tarjeta_date_update_checks_existing_issue_date(client):
    response = client.patch("/api/tarjetas/1", json={"fecha_vencimiento": "2000-01-01"})

    assert response.status_code == 400
    assert "fecha_vencimiento" in response.json()["detail"]


def vehiculo_payload(**overrides):
    payload = {
        "vin": "1HGCM82633A004353",
        "placa": "P124ABC",
        "id_tipo_vehiculo": 1,
        "id_marca": 1,
        "id_linea": 1,
        "modelo_anio": 2022,
        "id_color": 1,
        "numero_motor": "MOTOR-NUEVO",
        "numero_chasis": "CHASIS-NUEVO",
        "ejes": 2,
        "combustible": "GASOLINA",
        "uso": "PARTICULAR",
    }
    payload.update(overrides)
    return payload


def tarjeta_payload(**overrides):
    payload = {
        "id_vehiculo": 1,
        "id_propietario": 1,
        "numero_tarjeta": "TC-BASE-000002",
        "fecha_emision": str(date.today()),
        "fecha_vencimiento": str(date.today() + timedelta(days=365)),
        "estado": "VIGENTE",
        "id_usuario_emision": 1,
    }
    payload.update(overrides)
    return payload
