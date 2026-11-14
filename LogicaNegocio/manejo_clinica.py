from AccesoDatos.entidades import AtencionClinica
from AccesoDatos.repositorios import db
from LogicaNegocio.reglas_facturacion import ReglasFacturacion

class ManejoClinica:
    @staticmethod
    def cerrar_atencion_medica(id_atencion, cita, motivo, antecedentes, hallazgos, valoracion):
        cita.estado = "Atendido"
        atencion = AtencionClinica(id_atencion, cita, motivo, antecedentes, hallazgos, valoracion)
        db.guardar_atencion(atencion)
        cobro = ReglasFacturacion.generar_cobro_automatico(id_atencion, atencion)
        return atencion, cobro