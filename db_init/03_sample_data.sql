-- ============================================================
-- SAMPLE DATA: OWNERS, VEHICLES, AND CARDS
-- ============================================================

-- 1. Sample Propietario
INSERT INTO propietario (dpi, primer_nombre, primer_apellido, fecha_nacimiento, direccion, id_municipio, nit) VALUES
('1234567890101', 'Juan', 'Perez', '1985-05-20', 'Calle Real 10-10, Zona 1', 1, '1234567-8'),
('9876543210101', 'Maria', 'Garcia', '1992-10-15', 'Avenida Las Americas 5-20, Zona 14', 1, '8765432-1');

-- 2. Sample Vehiculos
-- Automovil Toyota Corolla para Juan
INSERT INTO vehiculo (vin, placa, id_tipo_vehiculo, id_marca, id_linea, modelo_anio, id_color, numero_motor, numero_chasis, cilindros, combustible, uso) VALUES
('ABC12345678901234', 'P-123ABC', 1, 1, 1, 2024, 1, 'MOTOR12345', 'CHASIS12345', 4, 'GASOLINA', 'PARTICULAR');

-- Motocicleta Honda para Maria
INSERT INTO vehiculo (vin, placa, id_tipo_vehiculo, id_marca, id_linea, modelo_anio, id_color, numero_motor, numero_chasis, cilindros, combustible, uso) VALUES
('XYZ98765432109876', 'M-456DEF', 2, 2, 4, 2023, 2, 'MOTOR98765', 'CHASIS98765', 1, 'GASOLINA', 'PARTICULAR');

-- 3. Sample Tarjetas de Circulacion
-- Tarjeta para el Corolla
INSERT INTO tarjeta_circulacion (id_vehiculo, id_propietario, numero_tarjeta, fecha_emision, fecha_vencimiento, estado, id_usuario_emision) VALUES
(1, 1, 'TC-2024-000001', CURRENT_DATE, CURRENT_DATE + INTERVAL '1 year', 'VIGENTE', 1);

-- Tarjeta para la Honda
INSERT INTO tarjeta_circulacion (id_vehiculo, id_propietario, numero_tarjeta, fecha_emision, fecha_vencimiento, estado, id_usuario_emision) VALUES
(2, 2, 'TC-2024-000002', CURRENT_DATE, CURRENT_DATE + INTERVAL '1 year', 'VIGENTE', 1);
