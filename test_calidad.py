import unittest
from datetime import datetime
from AccesoDatos.entidades import Medico, Paciente
from AccesoDatos.repositorios import db
from LogicaNegocio.servicios_agenda import ServicioAgenda

class PruebasCalidadSistema(unittest.TestCase):
    def setUp(self):
        db.database_url = None
        db.citas = []
        db.atenciones = []
        db.cobros = []
        self.medico = Medico(1, "Dr. Carlos Pérez", "carlos@mail.com", "123", 101, "General", 50000.0)
        self.paciente_valido = Paciente(1, "CC", "1035444555", "Mariana Agudelo", "3001234567")

    def test_cb_camino_1_hora_menor_limite(self):
        fecha = datetime(2026, 6, 10, 7, 0)
        self.assertFalse(ServicioAgenda.verificar_disponibilidad(self.medico, fecha))

    def test_cb_camino_2_hora_mayor_limite(self):
        fecha = datetime(2026, 6, 10, 19, 0)
        self.assertFalse(ServicioAgenda.verificar_disponibilidad(self.medico, fecha))

    def test_cb_camino_3_agenda_vacia_disponible(self):
        fecha = datetime(2026, 6, 10, 10, 0)
        self.assertTrue(ServicioAgenda.verificar_disponibilidad(self.medico, fecha))

    def test_cb_camino_4_cruce_horario_ocupado(self):
        fecha = datetime(2026, 6, 10, 10, 0)
        ServicioAgenda.asignar_cita(1, self.paciente_valido, self.medico, fecha)
        self.assertFalse(ServicioAgenda.verificar_disponibilidad(self.medico, fecha))

    def test_cb_camino_5_cita_previa_cancelada_permite_agendar(self):
        fecha = datetime(2026, 6, 10, 10, 0)
        ServicioAgenda.asignar_cita(1, self.paciente_valido, self.medico, fecha)
        db.citas[0].estado = "Cancelado"
        self.assertTrue(ServicioAgenda.verificar_disponibilidad(self.medico, fecha))

    def test_cn_particion_equivalencia_datos_erroneos(self):
        paciente_invalido = Paciente(2, "CC", "", "", "3000000000")
        fecha = datetime(2026, 6, 10, 11, 0)
        exito, _ = ServicioAgenda.asignar_cita(2, paciente_invalido, self.medico, fecha)
        self.assertFalse(exito)

    def test_cn_particion_equivalencia_datos_validos(self):
        fecha = datetime(2026, 6, 10, 11, 0)
        exito, _ = ServicioAgenda.asignar_cita(2, self.paciente_valido, self.medico, fecha)
        self.assertTrue(exito)

    def test_cn_valores_limite_horario(self):
        limite_inferior_invalido = datetime(2026, 6, 10, 7, 59)
        limite_inferior_valido = datetime(2026, 6, 10, 8, 0)
        limite_superior_valido = datetime(2026, 6, 10, 18, 0)
        limite_superior_invalido = datetime(2026, 6, 10, 18, 1)

        self.assertFalse(ServicioAgenda.verificar_disponibilidad(self.medico, limite_inferior_invalido))
        self.assertTrue(ServicioAgenda.verificar_disponibilidad(self.medico, limite_inferior_valido))
        self.assertTrue(ServicioAgenda.verificar_disponibilidad(self.medico, limite_superior_valido))
        self.assertFalse(ServicioAgenda.verificar_disponibilidad(self.medico, limite_superior_invalido))

if __name__ == "__main__":
    unittest.main()