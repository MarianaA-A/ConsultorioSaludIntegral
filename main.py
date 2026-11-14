from datetime import datetime
from AccesoDatos.entidades import Usuario, Paciente, Medico
from AccesoDatos.repositorios import db
from Presentacion.vistas import VistasRecepcion, VistasMedico

class Administrador(Usuario):
    def __init__(self, id_usuario, nombre, correo, contrasena, id_administrador):
        super().__init__(id_usuario, nombre, correo, contrasena, rol="Administrador")
        self.id_administrador = id_administrador

    def generar_reporte(self, cobros):
        print(f"\n[ADMIN - HTTPS] Generando reporte financiero...")
        total = sum(c.monto_total for c in cobros)
        print(f"Total ingresos consolidados en red privada: ${total:,.2f}")

if __name__ == "__main__":
    print("==================================================")
    print(" SISTEMA INTEGRAL - ARQUITECTURA DE TRES CAPAS ")
    print("==================================================\n")

    medico1 = Medico(1, "Dr. Carlos Pérez", "carlos@mail.com", "123", 101, "General", 50000.0)
    paciente1 = Paciente(1, "CC", "1035444555", "Mariana Agudelo", "3001234567")
    paciente2 = Paciente(2, "CC", "1038999888", "Alejandro Diez", "3109876543")

    horario = datetime(2026, 6, 10, 9, 30)

    print("--- 1. PROCESO DE RECEPCIÓN (HTTPS) ---")
    VistasRecepcion.agendar_cita(1, paciente1, medico1, horario, "Web")

    print("\n--- 2. PRUEBA DE REGLA DE NEGOCIO (EVITAR CRUCES) ---")
    VistasRecepcion.agendar_cita(2, paciente2, medico1, horario, "Telefono")

    print("\n--- 3. PROCESO MÉDICO Y COBRO AUTOMÁTICO ---")
    cita_guardada = db.citas[0]
    
    VistasMedico.consultar_y_atender(
        medico1, 
        horario, 
        cita_guardada, 
        "Control general", 
        "Ninguno", 
        "Estable", 
        "Sin novedad"
    )

    print("\n--- 4. MÓDULO ADMINISTRATIVO ---")
    admin = Administrador(4, "Mariana", "admin@mail.com", "123", 201)
    admin.generar_reporte(db.cobros)