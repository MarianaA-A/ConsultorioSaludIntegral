from AccesoDatos.entidades import Cobro
from AccesoDatos.repositorios import db

class ReglasFacturacion:
    @staticmethod
    def generar_cobro_automatico(id_cobro, atencion):
        monto = atencion.cita.medico.tarifa
        nuevo_cobro = Cobro(id_cobro, atencion, monto)
        db.guardar_cobro(nuevo_cobro)
        return nuevo_cobro