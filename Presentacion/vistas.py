from datetime import datetime
from flask import Flask, request, redirect, url_for, render_template_string
from AccesoDatos.entidades import Paciente
from AccesoDatos.repositorios import db
from LogicaNegocio.servicios_agenda import ServicioAgenda
from LogicaNegocio.manejo_clinica import ManejoClinica

PLANTILLA_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Consultorio Salud Integral - Portal HTTPS</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f4f7f9; margin: 0; padding: 20px; color: #333; }
        .header { background: #0d47a1; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .badge { background: #2e7d32; padding: 5px 10px; border-radius: 4px; font-size: 12px; display: inline-block; margin-top: 8px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        h2 { color: #0d47a1; margin-top: 0; border-bottom: 2px solid #e0e0e0; padding-bottom: 8px; }
        label { display: block; margin-top: 10px; font-weight: bold; font-size: 13px; }
        input, select { width: 100%; padding: 8px; margin-top: 4px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
        button { background: #0d47a1; color: white; border: none; padding: 10px 15px; border-radius: 4px; cursor: pointer; margin-top: 15px; font-weight: bold; }
        button:hover { background: #1565c0; }
        .btn-atender { background: #2e7d32; margin-top: 8px; }
        .alerta { padding: 12px; border-radius: 5px; margin-bottom: 20px; font-weight: bold; }
        .ok { background: #e8f5e9; color: #2e7d32; border: 1px solid #a5d6a7; }
        .error { background: #ffebee; color: #c62828; border: 1px solid #ef9a9a; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background: #e3f2fd; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Consultorio Médico "Salud Integral"</h1>
        <div>Acceso Seguro HTTPS — Recepción y Consultorios Médicos</div>
        <div class="badge">{{ estado_bd }}</div>
    </div>

    {% if mensaje %}
    <div class="alerta {{ tipo_mensaje }}">{{ mensaje }}</div>
    {% endif %}

    <div class="grid">
        <div class="card">
            <h2>1. Módulo de Recepción (Agendamiento)</h2>
            <form method="POST" action="/agendar">
                <label>Tipo de Documento</label>
                <select name="tipo_doc">
                    <option value="CC">Cédula de Ciudadanía (CC)</option>
                    <option value="TI">Tarjeta de Identidad (TI)</option>
                    <option value="CE">Cédula de Extranjería (CE)</option>
                </select>
                <label>Número de Documento</label>
                <input type="text" name="num_doc" required>
                <label>Nombre Completo del Paciente</label>
                <input type="text" name="nombre" required>
                <label>Teléfono</label>
                <input type="text" name="telefono" required>
                <label>Consultorio / Especialista</label>
                <select name="id_medico">
                    {% for m in medicos %}
                    <option value="{{ m.id_medico }}">{{ m.nombre }} - {{ m.especialidad }} (${{ "{:,.0f}".format(m.tarifa) }})</option>
                    {% endfor %}
                </select>
                <label>Fecha y Hora de Cita</label>
                <input type="datetime-local" name="fecha_hora" required>
                <label>Canal de Solicitud</label>
                <select name="origen">
                    <option value="Web">Web</option>
                    <option value="Telefono">Teléfono</option>
                </select>
                <button type="submit">Verificar Disponibilidad y Agendar</button>
            </form>
        </div>

        <div class="card">
            <h2>2. Consultorios Médicos (Atención y Cierre)</h2>
            {% if citas %}
                {% for c in citas %}
                <div style="border: 1px solid #ddd; padding: 10px; border-radius: 6px; margin-bottom: 12px;">
                    <strong>{{ c.fecha.strftime('%Y-%m-%d %H:%M') }}</strong> | {{ c.paciente.nombre }} ({{ c.paciente.num_doc }})<br>
                    Especialidad: {{ c.medico.especialidad }} ({{ c.medico.nombre }}) | Estado: <strong>{{ c.estado }}</strong>
                    {% if c.estado == 'Ocupado' %}
                    <form method="POST" action="/atender/{{ c.id_cita }}">
                        <input type="text" name="motivo" placeholder="Motivo de consulta" required>
                        <input type="text" name="antecedentes" placeholder="Antecedentes clínicos" required>
                        <input type="text" name="hallazgos" placeholder="Hallazgos físicos" required>
                        <input type="text" name="valoracion" placeholder="Valoración y diagnóstico" required>
                        <button type="submit" class="btn-atender">Cerrar Atención y Generar Cobro Automático</button>
                    </form>
                    {% endif %}
                </div>
                {% endfor %}
            {% else %}
                <p>No hay citas registradas en la agenda.</p>
            {% endif %}
        </div>
    </div>

    <div class="card" style="margin-top: 20px;">
        <h2>3. Facturación Automática (Interfaz Provista)</h2>
        <table>
            <tr>
                <th>Factura #</th>
                <th>Fecha Emisión</th>
                <th>Paciente</th>
                <th>Especialidad</th>
                <th>Monto Cobrado</th>
                <th>Estado</th>
            </tr>
            {% for cobro in cobros %}
            <tr>
                <td>{{ cobro.id_cobro }}</td>
                <td>{{ cobro.fecha }}</td>
                <td>{{ cobro.paciente }}</td>
                <td>{{ cobro.especialidad }}</td>
                <td>${{ "{:,.2f}".format(cobro.monto) }}</td>
                <td>{{ cobro.estado }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""

class VistasRecepcion:
    @staticmethod
    def agendar_cita(id_cita, paciente, medico, fecha, origen):
        exito, mensaje = ServicioAgenda.asignar_cita(id_cita, paciente, medico, fecha, origen)
        return exito, mensaje

class VistasMedico:
    @staticmethod
    def consultar_y_atender(medico, fecha, cita, motivo, antecedentes, hallazgos, valoracion):
        return ManejoClinica.cerrar_atencion_medica(1, cita, motivo, antecedentes, hallazgos, valoracion)

def crear_aplicacion_web():
    app = Flask(__name__)

    @app.route("/", methods=["GET"])
    def inicio():
        mensaje = request.args.get("mensaje")
        tipo_mensaje = request.args.get("tipo", "ok")
        estado_bd = "Persistencia: PostgreSQL en Red Privada Activa" if db.database_url else "Persistencia: Modo Local"
        return render_template_string(
            PLANTILLA_HTML,
            medicos=db.medicos,
            citas=db.obtener_todas_las_citas(),
            cobros=db.obtener_todos_los_cobros(),
            mensaje=mensaje,
            tipo_mensaje=tipo_mensaje,
            estado_bd=estado_bd
        )

    @app.route("/agendar", methods=["POST"])
    def agendar():
        paciente = Paciente(
            0,
            request.form["tipo_doc"],
            request.form["num_doc"],
            request.form["nombre"],
            request.form["telefono"]
        )
        medico = db.obtener_medico_por_id(request.form["id_medico"])
        fecha = datetime.strptime(request.form["fecha_hora"], "%Y-%m-%dT%H:%M")
        origen = request.form["origen"]
        exito, mensaje = VistasRecepcion.agendar_cita(0, paciente, medico, fecha, origen)
        tipo = "ok" if exito else "error"
        return redirect(url_for("inicio", mensaje=mensaje, tipo=tipo))

    @app.route("/atender/<int:id_cita>", methods=["POST"])
    def atender(id_cita):
        todas = db.obtener_todas_las_citas()
        cita_objetivo = next((c for c in todas if c.id_cita == id_cita), None)
        if cita_objetivo:
            _, cobro = VistasMedico.consultar_y_atender(
                cita_objetivo.medico,
                cita_objetivo.fecha,
                cita_objetivo,
                request.form["motivo"],
                request.form["antecedentes"],
                request.form["hallazgos"],
                request.form["valoracion"]
            )
            msg = f"Atención cerrada. Cobro #{cobro.id_cobro} generado automáticamente por ${cobro.monto_total:,.2f}"
            return redirect(url_for("inicio", mensaje=msg, tipo="ok"))
        return redirect(url_for("inicio", mensaje="Cita no encontrada", tipo="error"))

    return app