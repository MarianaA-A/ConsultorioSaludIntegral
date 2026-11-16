import os
from datetime import datetime
from AccesoDatos.entidades import Paciente, Medico, Cita, AtencionClinica, Cobro

try:
    import psycopg2
except ImportError:
    psycopg2 = None

class RepositorioSistema:
    def __init__(self):
        self.database_url = os.environ.get("DATABASE_URL")
        self.usuarios = []
        self.pacientes = []
        self.medicos = [
            Medico(1, "Dr. Carlos Pérez", "carlos@saludintegral.com", "123", 1, "General", 50000.0),
            Medico(2, "Dra. Laura Gómez", "laura@saludintegral.com", "123", 2, "Odontologia", 70000.0),
            Medico(3, "Dr. Andrés Silva", "andres@saludintegral.com", "123", 3, "Pediatria", 60000.0)
        ]
        self.citas = []
        self.atenciones = []
        self.cobros = []
        if self.database_url and psycopg2:
            self.inicializar_postgresql()

    def conectar(self):
        return psycopg2.connect(self.database_url)

    def inicializar_postgresql(self):
        conn = self.conectar()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id_usuario SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                correo VARCHAR(150) UNIQUE NOT NULL,
                contrasena VARCHAR(255) NOT NULL,
                rol VARCHAR(50) NOT NULL
            );
            CREATE TABLE IF NOT EXISTS pacientes (
                id_paciente SERIAL PRIMARY KEY,
                tipo_doc VARCHAR(10) NOT NULL,
                num_doc VARCHAR(20) UNIQUE NOT NULL,
                nombre VARCHAR(100) NOT NULL,
                telefono VARCHAR(20) NOT NULL
            );
            CREATE TABLE IF NOT EXISTS medicos (
                id_medico SERIAL PRIMARY KEY,
                id_usuario INT REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
                especialidad VARCHAR(50) NOT NULL,
                tarifa_base NUMERIC(12, 2) NOT NULL
            );
            CREATE TABLE IF NOT EXISTS citas (
                id_cita SERIAL PRIMARY KEY,
                id_paciente INT REFERENCES pacientes(id_paciente) ON DELETE RESTRICT,
                id_medico INT REFERENCES medicos(id_medico) ON DELETE RESTRICT,
                fecha_hora TIMESTAMP NOT NULL,
                estado VARCHAR(30) NOT NULL DEFAULT 'Disponible',
                origen VARCHAR(20) NOT NULL DEFAULT 'Web'
            );
            CREATE TABLE IF NOT EXISTS atencion_clinica (
                id_atencion SERIAL PRIMARY KEY,
                id_cita INT REFERENCES citas(id_cita) ON DELETE CASCADE,
                motivo TEXT NOT NULL,
                antecedentes TEXT,
                hallazgos TEXT NOT NULL,
                valoracion TEXT NOT NULL,
                fecha_atencion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS cobros (
                id_cobro SERIAL PRIMARY KEY,
                id_atencion INT REFERENCES atencion_clinica(id_atencion) ON DELETE CASCADE,
                monto_total NUMERIC(12, 2) NOT NULL,
                estado_pago VARCHAR(20) NOT NULL DEFAULT 'Pagado',
                fecha_emision TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cur.execute("SELECT COUNT(*) FROM medicos;")
        if cur.fetchone()[0] == 0:
            for m in self.medicos:
                cur.execute(
                    "INSERT INTO usuarios (nombre, correo, contrasena, rol) VALUES (%s, %s, %s, %s) RETURNING id_usuario;",
                    (m.nombre, m.correo, m.contrasena, "Medico")
                )
                id_u = cur.fetchone()[0]
                cur.execute(
                    "INSERT INTO medicos (id_usuario, especialidad, tarifa_base) VALUES (%s, %s, %s);",
                    (id_u, m.especialidad, m.tarifa)
                )
        conn.commit()
        cur.close()
        conn.close()

    def obtener_medico_por_id(self, id_medico):
        for m in self.medicos:
            if m.id_medico == int(id_medico):
                return m
        return self.medicos[0]

    def guardar_cita(self, cita):
        if self.database_url and psycopg2:
            conn = self.conectar()
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO pacientes (tipo_doc, num_doc, nombre, telefono)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (num_doc) DO UPDATE SET nombre = EXCLUDED.nombre, telefono = EXCLUDED.telefono
                RETURNING id_paciente;
                """,
                (cita.paciente.tipo_doc, cita.paciente.num_doc, cita.paciente.nombre, cita.paciente.telefono)
            )
            id_pac = cur.fetchone()[0]
            cita.paciente.id_paciente = id_pac
            cur.execute(
                """
                INSERT INTO citas (id_paciente, id_medico, fecha_hora, estado, origen)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id_cita;
                """,
                (id_pac, cita.medico.id_medico, cita.fecha, cita.estado, cita.origen)
            )
            cita.id_cita = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
        else:
            cita.id_cita = len(self.citas) + 1
            self.citas.append(cita)

    def obtener_citas_medico(self, id_medico, fecha):
        if self.database_url and psycopg2:
            conn = self.conectar()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT c.id_cita, c.fecha_hora, c.estado, c.origen,
                       p.id_paciente, p.tipo_doc, p.num_doc, p.nombre, p.telefono
                FROM citas c
                JOIN pacientes p ON c.id_paciente = p.id_paciente
                WHERE c.id_medico = %s AND DATE(c.fecha_hora) = %s;
                """,
                (id_medico, fecha.date())
            )
            filas = cur.fetchall()
            cur.close()
            conn.close()
            medico = self.obtener_medico_por_id(id_medico)
            resultado = []
            for f in filas:
                pac = Paciente(f[4], f[5], f[6], f[7], f[8])
                cita_obj = Cita(f[0], pac, medico, f[1], f[3])
                cita_obj.estado = f[2]
                resultado.append(cita_obj)
            return resultado
        return [c for c in self.citas if c.medico.id_medico == id_medico and c.fecha.date() == fecha.date()]

    def obtener_todas_las_citas(self):
        if self.database_url and psycopg2:
            conn = self.conectar()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT c.id_cita, c.id_medico, c.fecha_hora, c.estado, c.origen,
                       p.id_paciente, p.tipo_doc, p.num_doc, p.nombre, p.telefono
                FROM citas c
                JOIN pacientes p ON c.id_paciente = p.id_paciente
                ORDER BY c.fecha_hora ASC;
                """
            )
            filas = cur.fetchall()
            cur.close()
            conn.close()
            resultado = []
            for f in filas:
                med = self.obtener_medico_por_id(f[1])
                pac = Paciente(f[5], f[6], f[7], f[8], f[9])
                cita_obj = Cita(f[0], pac, med, f[2], f[4])
                cita_obj.estado = f[3]
                resultado.append(cita_obj)
            return resultado
        return self.citas

    def guardar_atencion(self, atencion):
        if self.database_url and psycopg2:
            conn = self.conectar()
            cur = conn.cursor()
            cur.execute("UPDATE citas SET estado = 'Atendido' WHERE id_cita = %s;", (atencion.cita.id_cita,))
            cur.execute(
                """
                INSERT INTO atencion_clinica (id_cita, motivo, antecedentes, hallazgos, valoracion)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id_atencion;
                """,
                (atencion.cita.id_cita, atencion.motivo, atencion.antecedentes, atencion.hallazgos, atencion.valoracion)
            )
            atencion.id_atencion = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
        else:
            atencion.id_atencion = len(self.atenciones) + 1
            self.atenciones.append(atencion)

    def guardar_cobro(self, cobro):
        if self.database_url and psycopg2:
            conn = self.conectar()
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO cobros (id_atencion, monto_total, estado_pago)
                VALUES (%s, %s, %s)
                RETURNING id_cobro;
                """,
                (cobro.atencion.id_atencion, cobro.monto_total, cobro.estado_pago)
            )
            cobro.id_cobro = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
        else:
            cobro.id_cobro = len(self.cobros) + 1
            self.cobros.append(cobro)

    def obtener_todos_los_cobros(self):
        if self.database_url and psycopg2:
            conn = self.conectar()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT cb.id_cobro, cb.monto_total, cb.estado_pago, cb.fecha_emision,
                       p.nombre, m.especialidad
                FROM cobros cb
                JOIN atencion_clinica a ON cb.id_atencion = a.id_atencion
                JOIN citas c ON a.id_cita = c.id_cita
                JOIN pacientes p ON c.id_paciente = p.id_paciente
                JOIN medicos m ON c.id_medico = m.id_medico
                ORDER BY cb.id_cobro DESC;
                """
            )
            filas = cur.fetchall()
            cur.close()
            conn.close()
            return [
                {
                    "id_cobro": f[0],
                    "monto": float(f[1]),
                    "estado": f[2],
                    "fecha": f[3].strftime("%Y-%m-%d %H:%M"),
                    "paciente": f[4],
                    "especialidad": f[5]
                }
                for f in filas
            ]
        return [
            {
                "id_cobro": cb.id_cobro,
                "monto": cb.monto_total,
                "estado": cb.estado_pago,
                "fecha": cb.fecha_emision.strftime("%Y-%m-%d %H:%M"),
                "paciente": cb.atencion.cita.paciente.nombre,
                "especialidad": cb.atencion.cita.medico.especialidad
            }
            for cb in self.cobros
        ]

db = RepositorioSistema()