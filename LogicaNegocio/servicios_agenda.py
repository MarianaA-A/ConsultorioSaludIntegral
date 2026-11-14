from AccesoDatos.entidades import Cita
from AccesoDatos.repositorios import db

class ServicioAgenda:
    @staticmethod
    def verificar_disponibilidad(medico, fecha):
        citas_existentes = db.obtener_citas_medico(medico.id_medico, fecha)
        for c in citas_existentes:
            if c.fecha == fecha and c.estado != "Cancelado":
                return False
        return True

    @staticmethod
    def asignar_cita(id_cita, paciente, medico, fecha, origen="Web"):
        if ServicioAgenda.verificar_disponibilidad(medico, fecha):
            nueva_cita = Cita(id_cita, paciente, medico, fecha, origen)
            nueva_cita.estado = "Ocupado"
            db.guardar_cita(nueva_cita)
            return True, "Cita asignada exitosamente."
        return False, "Error: El horario ya fue asignado o el médico está ocupado."