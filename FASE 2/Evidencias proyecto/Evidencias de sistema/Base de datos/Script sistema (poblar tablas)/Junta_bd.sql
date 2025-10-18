-- Crear Base de Datosactividad
CREATE DATABASE IF NOT EXISTS junta_vecinal;
USE junta_vecinal;

/* BORRADO DE LAS TABLAS SI YA ESTÁN CREADAS */
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS rol;
DROP TABLE IF EXISTS vecino;
DROP TABLE IF EXISTS certificado;
DROP TABLE IF EXISTS proyecto;
DROP TABLE IF EXISTS noticia;
DROP TABLE IF EXISTS espacio_comunal;
DROP TABLE IF EXISTS reserva;
DROP TABLE IF EXISTS actividad;
DROP TABLE IF EXISTS inscripcion_actividad;
DROP TABLE IF EXISTS solicitud;
DROP TABLE IF EXISTS auditoria;
DROP TABLE IF EXISTS documento;
DROP TABLE IF EXISTS metricas;

SET FOREIGN_KEY_CHECKS = 1;



-- Tabla de Roles
CREATE TABLE rol (
    id_rol INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
);

-- Tabla de Vecinos
CREATE TABLE vecino (
    id_vecino INT AUTO_INCREMENT PRIMARY KEY,
    run VARCHAR(15) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(200),
    correo VARCHAR(100) UNIQUE,
    telefono VARCHAR(20),
    contrasena VARCHAR(255) NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    id_rol INT NOT NULL,
    estado ENUM('Activo', 'Rechazado', 'Pendiente', 'Desactivado') DEFAULT 'Pendiente',
    foto VARCHAR(200) DEFAULT 'perfiles/Default.png',
    evidencia VARCHAR(255),
    FOREIGN KEY (id_rol) REFERENCES rol(id_rol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;





-- Tabla de Certificadosjunta_vecinal
CREATE TABLE certificado (
    id_certificado INT AUTO_INCREMENT PRIMARY KEY,
    id_vecino INT NOT NULL,
    tipo ENUM('Residencia') DEFAULT 'Residencia',
    fecha_emision TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    folio VARCHAR(50) UNIQUE,
    qr_code VARCHAR(255),
    firma_digital VARCHAR(255),
    estado ENUM('Pendiente','Emitido','Rechazado') DEFAULT 'Pendiente',
    FOREIGN KEY (id_vecino) REFERENCES vecino(id_vecino)
);

-- Tabla de Proyectos Vecinales
CREATE TABLE proyecto (
    id_proyecto INT AUTO_INCREMENT PRIMARY KEY,
    id_vecino INT NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT,
    presupuesto DECIMAL(12,2),
    documento_adj VARCHAR(255),
    fecha_postulacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado ENUM('En Revisión','Aprobado','Rechazado') DEFAULT 'En Revisión',
    FOREIGN KEY (id_vecino) REFERENCES vecino(id_vecino)
);

-- Tabla de Noticias
CREATE TABLE noticia (
    id_noticia INT AUTO_INCREMENT PRIMARY KEY,
    id_autor INT NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    contenido TEXT,
    fecha_publicacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_autor) REFERENCES vecino(id_vecino)
);

-- Tabla de Espacios comunales
CREATE TABLE espacio_comunal (
    id_espacio INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255),
    monto_hora INT DEFAULT 0,
    imagen VARCHAR(200),
    estado ENUM('Activo','Inactivo') DEFAULT 'Activo',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Tabla de Reservas de Espacios
CREATE TABLE reserva (
    id_reserva INT AUTO_INCREMENT PRIMARY KEY,
    id_vecino INT NOT NULL,
    id_espacio INT NOT NULL,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    estado ENUM('Activa', 'Cancelada') DEFAULT 'Activa',
    observacion VARCHAR(255),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total INT,
    FOREIGN KEY (id_vecino) REFERENCES vecino(id_vecino),
    FOREIGN KEY (id_espacio) REFERENCES espacio_comunal(id_espacio)
);

-- Tabla de Actividades
CREATE TABLE actividad (
    id_actividad INT AUTO_INCREMENT PRIMARY KEY,
    id_vecino INT NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    ubicacion VARCHAR(200) NOT NULL,
    descripcion TEXT,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    cupos INT,
    estado ENUM('Activa','Finalizada','Cancelada') DEFAULT 'Activa',
    FOREIGN KEY (id_vecino) REFERENCES vecino(id_vecino)
);

-- Relación inscripción a actividades
CREATE TABLE inscripcion_actividad (
    id_inscripcion INT AUTO_INCREMENT PRIMARY KEY,
    id_actividad INT NOT NULL,
    id_vecino INT NOT NULL,
    fecha_inscripcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_actividad) REFERENCES actividad(id_actividad),
    FOREIGN KEY (id_vecino) REFERENCES vecino(id_vecino),
    UNIQUE (id_actividad, id_vecino) -- evita doble inscripción
);

-- Tabla de Solicitudes Ciudadanas
CREATE TABLE solicitud (
    id_solicitud INT AUTO_INCREMENT PRIMARY KEY,
    id_vecino INT NOT NULL,
    tipo ENUM('Mantención','Luminarias','Aseo','Otro') DEFAULT 'Otro',
    descripcion TEXT,
    estado ENUM('Pendiente','En Proceso','Resuelta','Rechazada') DEFAULT 'Pendiente',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_vecino) REFERENCES vecino(id_vecino)
);

-- Tabla de Bitácora / Auditoría
CREATE TABLE auditoria (
    id_evento INT AUTO_INCREMENT PRIMARY KEY,
    id_vecino INT,
    accion VARCHAR(255) NOT NULL,
    fecha_evento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resultado VARCHAR(255),
    FOREIGN KEY (id_vecino) REFERENCES vecino(id_vecino)
);

-- Tabla de Documentos
CREATE TABLE documento (
    id_documento INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    tipo ENUM('Acta','Estatuto','Reglamento','Oficio') DEFAULT 'Acta',
    ruta_archivo VARCHAR(255),
    version INT DEFAULT 1,
    fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Métricas Básicas (ejemplo simplificado)
CREATE TABLE metricas (
    id_metrica INT AUTO_INCREMENT PRIMARY KEY,
    descripcion VARCHAR(200),
    valor DECIMAL(12,2),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


INSERT INTO rol VALUES (1,"vecino");
INSERT INTO rol VALUES (2,"secretario");
INSERT INTO rol VALUES (3,"tesorero");
INSERT INTO rol VALUES (4,"presidente");

-- SELECT * FROM `rol` LIMIT 1000

-- Presidente
INSERT INTO vecino (run, nombre, direccion, correo, telefono, contrasena, id_rol, estado)
VALUES (
  '11.111.111-1',
  'Felipe Presidente',
  'Av. Central 123',
  'felipe.presidente@gmail.com',
  '987654321',
  'pbkdf2_sha256$1000000$gZxpz5ArIF3lWm4wjqKSdH$YAdQFsiTmv6rKcjeG09WYdXxh4YGtUHl2/GfhQB9bLM=',
  4,
  'Activo'
);

-- Secretario
INSERT INTO vecino (run, nombre, direccion, correo, telefono, contrasena, id_rol, estado)
VALUES (
  '22.222.222-2',
  'María Secretaria',
  'Calle Los Álamos 321',
  'maria.secretaria@gmail.com',
  '987654322',
  'pbkdf2_sha256$1000000$aZiZNizT62QGvZ0OxMsmmQ$p2dKLzkySZ2w3yOTeMCUSjThCdzYGrZx3VPKb8n0Pis=',
  2,
  'Activo'
);

-- Tesorero
INSERT INTO vecino (run, nombre, direccion, correo, telefono, contrasena, id_rol, estado)
VALUES (
  '33.333.333-3',
  'José Tesorero',
  'Pasaje 45 Oriente',
  'jose.tesorero@gmail.com',
  '987654323',
  'pbkdf2_sha256$1000000$hOdyD0ySCiqxu11jU9l7M1$MOOUdtX6Z4YxJlwsxEYfQO0AZFkkd0G8FJKN+6tCp7U=',
  3,
  'Activo'
);

-- Vecino 1
INSERT INTO vecino (run, nombre, direccion, correo, telefono, contrasena, id_rol, estado)
VALUES (
  '44.444.444-4',
  'Ana Vecina',
  'Av. del Bosque 456',
  'ana.vecina@gmail.com',
  '987654324',
  'pbkdf2_sha256$1000000$WlKLmWSUzBIAP79C29ssaA$igp0QWg9CcxhNo9ab9IttUE8cW9GdCGn57s+uTD6NPA=',
  1,
  'Activo'
);

-- Vecino 2
INSERT INTO vecino (run, nombre, direccion, correo, telefono, contrasena, id_rol, estado)
VALUES (
  '55.555.555-5',
  'Carlos Vecino',
  'Villa Los Robles 789',
  'carlos.vecino@gmail.com',
  '987654325',
  'pbkdf2_sha256$1000000$WlKLmWSUzBIAP79C29ssaA$igp0QWg9CcxhNo9ab9IttUE8cW9GdCGn57s+uTD6NPA=',
  1,
  'Activo'
);

INSERT INTO espacio_comunal 
(nombre, descripcion, monto_hora, imagen, estado, fecha_creacion)
VALUES
('Parque Central', 'Área verde ideal para eventos al aire libre y actividades familiares.', 1500, 'espacios/Parque.jpeg', 'Activo', NOW()),
('Sede Vecinal', 'Espacio cerrado con sillas, mesas y cocina, ideal para reuniones comunitarias.', 2500, 'espacios/SedeVecinos.jpg', 'Activo', NOW()),
('Cancha Multiuso', 'Cancha techada para fútbol, básquetbol y vóleibol, con iluminación nocturna.', 2000, 'espacios/Cancha.png', 'Activo', NOW());



-- === RESERVAS PARA MAÑANA ===
INSERT INTO reserva (id_vecino, id_espacio, fecha, hora_inicio, hora_fin, estado, observacion, total)
VALUES
(4, 1, DATE_ADD(CURDATE(), INTERVAL 1 DAY), '10:00', '12:00', 'Activa', 'Reserva matutina en el Parque Central', 3000),
(5, 2, DATE_ADD(CURDATE(), INTERVAL 1 DAY), '14:00', '16:00', 'Activa', 'Reunión en la Sede Vecinal', 5000),
(3, 3, DATE_ADD(CURDATE(), INTERVAL 1 DAY), '18:00', '20:00', 'Activa', 'Entrenamiento en Cancha Multiuso', 4000);



-- === ACTIVIDADES ACTIVAS (vinculadas a las reservas de mañana) ===
INSERT INTO actividad (id_vecino, titulo, ubicacion, descripcion, fecha, hora_inicio, hora_fin, cupos, estado)
VALUES
(4, 'Taller de Jardinería', 'Parque Central', 'Aprende sobre el cuidado de plantas y compostaje.', DATE_ADD(CURDATE(), INTERVAL 1 DAY), '10:00', '12:00', 20, 'Activa'),
(5, 'Reunión de Comité Vecinal', 'Sede Vecinal', 'Conversaremos los nuevos proyectos del barrio.', DATE_ADD(CURDATE(), INTERVAL 1 DAY), '14:00', '16:00', 15, 'Activa'),
(3, 'Campeonato de Baby Fútbol', 'Cancha Multiuso', 'Participa en un entretenido campeonato local.', DATE_ADD(CURDATE(), INTERVAL 1 DAY), '18:00', '20:00', 30, 'Activa');


-- === ACTIVIDAD FINALIZADA ===
INSERT INTO actividad (id_vecino, titulo, ubicacion, descripcion, fecha, hora_inicio, hora_fin, cupos, estado)
VALUES
(2, 'Charla sobre Reciclaje', 'Sede Vecinal', 'Concientización sobre reciclaje y reducción de residuos.', DATE_SUB(CURDATE(), INTERVAL 1 DAY), '11:00', '13:00', 25, 'Finalizada');

-- === ACTIVIDAD CANCELADA ===
INSERT INTO actividad (id_vecino, titulo, ubicacion, descripcion, fecha, hora_inicio, hora_fin, cupos, estado)
VALUES
(1, 'Clase de Yoga', 'Parque Central', 'Sesión abierta de yoga para vecinos.', DATE_ADD(CURDATE(), INTERVAL 1 DAY), '09:00', '10:00', 20, 'Cancelada');


-- SELECT * FROM `vecino` LIMIT 1000