import os
from Presentacion.vistas import crear_aplicacion_web

app = crear_aplicacion_web()

if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=puerto)