DROP TABLE IF EXISTS cobros CASCADE;
DROP TABLE IF EXISTS atencion_clinica CASCADE;
DROP TABLE IF EXISTS citas CASCADE;
DROP TABLE IF EXISTS medicos CASCADE;
DROP TABLE IF EXISTS pacientes CASCADE;
DROP TABLE IF EXISTS usuarios CASCADE;

CREATE TABLE usuarios (
    id_usuario SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(150) UNIQUE NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    rol VARCHAR(50) NOT NULL CHECK (rol IN ('Recepcion', 'Medico', 'Administrador'))
);

CREATE TABLE pacientes (
    id_paciente SERIAL PRIMARY KEY,
    tipo_doc VARCHAR(10) NOT NULL,
    num_doc VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) NOT NULL
);

CREATE TABLE medicos (
    id_medico SERIAL PRIMARY KEY,
    id_usuario INT REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    especialidad VARCHAR(50) NOT NULL CHECK (especialidad IN ('General', 'Odontologia', 'Pediatria')),
    tarifa_base NUMERIC(12, 2) NOT NULL
);

CREATE TABLE citas (
    id_cita SERIAL PRIMARY KEY,
    id_paciente INT REFERENCES pacientes(id_paciente) ON DELETE RESTRICT,
    id_medico INT REFERENCES medicos(id_medico) ON DELETE RESTRICT,
    fecha_hora TIMESTAMP NOT NULL,
    estado VARCHAR(30) NOT NULL DEFAULT 'Disponible' CHECK (estado IN ('Disponible', 'Ocupado', 'Atendido', 'Cancelado')),
    origen VARCHAR(20) NOT NULL DEFAULT 'Web' CHECK (origen IN ('Web', 'Telefono'))
);

CREATE TABLE atencion_clinica (
    id_atencion SERIAL PRIMARY KEY,
    id_cita INT REFERENCES citas(id_cita) ON DELETE CASCADE,
    motivo TEXT NOT NULL,
    antecedentes TEXT,
    hallazgos TEXT NOT NULL,
    valoracion TEXT NOT NULL,
    fecha_atencion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cobros (
    id_id_cobro SERIAL PRIMARY KEY,
    id_atencion INT REFERENCES atencion_clinica(id_atencion) ON DELETE CASCADE,
    monto_total NUMERIC(12, 2) NOT NULL,
    estado_pago VARCHAR(20) NOT NULL DEFAULT 'Pagado' CHECK (estado_pago IN ('Pendiente', 'Pagado', 'Anulado')),
    fecha_emision TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_citas_medico_fecha ON citas(id_medico, fecha_hora);
CREATE INDEX idx_cobros_fecha ON cobros(fecha_emision);