class BaseDatosMemoria:
    def __init__(self):
        self.usuarios = []
        self.pacientes = []
        self.citas = []
        self.atenciones = []
        self.cobros = []

    def guardar_cita(self, cita):
        self.citas.append(cita)

    def obtener_citas_medico(self, id_medico, fecha):
        return [c for c in self.citas if c.medico.id_medico == id_medico and c.fecha.date() == fecha.date()]

    def guardar_atencion(self, atencion):
        self.atenciones.append(atencion)

    def guardar_cobro(self, cobro):
        self.cobros.append(cobro)

db = BaseDatosMemoria()