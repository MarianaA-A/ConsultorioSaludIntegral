from datetime import datetime

class Usuario:
    def __init__(self, id_usuario, nombre, correo, contrasena, rol):
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.correo = correo
        self.contrasena = contrasena
        self.rol = rol

class Paciente:
    def __init__(self, id_paciente, tipo_doc, num_doc, nombre, telefono):
        self.id_paciente = id_paciente
        self.tipo_doc = tipo_doc
        self.num_doc = num_doc
        self.nombre = nombre
        self.telefono = telefono

class Cita:
    def __init__(self, id_cita, paciente, medico, fecha, origen="Web"):
        self.id_cita = id_cita
        self.paciente = paciente
        self.medico = medico
        self.fecha = fecha
        self.estado = "Disponible"
        self.origen = origen

class AtencionClinica:
    def __init__(self, id_atencion, cita, motivo, antecedentes, hallazgos, valoracion):
        self.id_atencion = id_atencion
        self.cita = cita
        self.motivo = motivo
        self.antecedentes = antecedentes
        self.hallazgos = hallazgos
        self.valoracion = valoracion
        self.fecha_atencion = datetime.now()

class Cobro:
    def __init__(self, id_cobro, atencion, monto):
        self.id_cobro = id_cobro
        self.atencion = atencion
        self.monto_total = monto
        self.estado_pago = "Pagado"
        self.fecha_emision = datetime.now()