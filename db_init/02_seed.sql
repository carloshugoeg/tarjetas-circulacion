-- ============================================================
-- SEED DATA FOR CATALOGS
-- ============================================================

-- Departamentos
INSERT INTO departamento (nombre, codigo) VALUES
('Guatemala', '01'),
('Sacatepéquez', '03'),
('Quetzaltenango', '09');

-- Municipios
INSERT INTO municipio (id_departamento, nombre) VALUES
(1, 'Guatemala'),
(1, 'Mixco'),
(1, 'Villa Nueva'),
(2, 'Antigua Guatemala'),
(3, 'Quetzaltenango');

-- Tipos de Vehículo
INSERT INTO tipo_vehiculo (nombre, descripcion) VALUES
('Automóvil', 'Vehículo ligero de 4 ruedas para transporte de personas'),
('Motocicleta', 'Vehículo de 2 ruedas'),
('Camión', 'Vehículo pesado para transporte de carga');

-- Marcas
INSERT INTO marca_vehiculo (nombre) VALUES
('Toyota'),
('Honda'),
('Nissan'),
('Hyundai'),
('Mazda');

-- Líneas
INSERT INTO linea_vehiculo (id_marca, nombre) VALUES
(1, 'Corolla'),
(1, 'Hilux'),
(1, 'Yaris'),
(2, 'Civic'),
(2, 'CR-V'),
(3, 'Sentra'),
(4, 'Tucson'),
(5, 'Mazda 3');

-- Colores
INSERT INTO color (nombre) VALUES
('Blanco'),
('Negro'),
('Gris'),
('Plata'),
('Rojo'),
('Azul');

-- Usuarios del Sistema (Para pruebas iniciales)
INSERT INTO usuario_sistema (username, nombre_completo) VALUES
('admin', 'Administrador del Sistema'),
('hescobar', 'Hugo Escobar');
