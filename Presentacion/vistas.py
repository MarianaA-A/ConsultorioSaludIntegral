from LogicaNegocio.servicios_agenda import ServicioAgenda
from LogicaNegocio.manejo_clinica import ManejoClinica
from AccesoDatos.repositorios import db

class VistasRecepcion:
    @staticmethod
    def agendar_cita(id_cita, paciente, medico, fecha, origen):
        exito, mensaje = ServicioAgenda.asignar_cita(id_cita, paciente, medico, fecha, origen)
        print(f"[RECEPCIÓN - HTTPS] {mensaje}")
        return exito

class VistasMedico:
    @staticmethod
    def consultar_y_atender(medico, fecha, cita, motivo, antecedentes, hallazgos, valoracion):
        print(f"\n[MÉDICO - HTTPS] Consultando agenda de {medico.nombre}...")
        citas = db.obtener_citas_medico(medico.id_medico, fecha)
        for c in citas:
            print(f"-> Hora: {c.fecha.strftime('%H:%M')} | Paciente: {c.paciente.nombre} | Estado: {c.estado}")
        
        atencion, cobro = ManejoClinica.cerrar_atencion_medica(1, cita, motivo, antecedentes, hallazgos, valoracion)
        print(f"[INTERFAZ PROVISTA] Atención cerrada. Factura #{cobro.id_cobro} emitida por ${cobro.monto_total:,.2f}")