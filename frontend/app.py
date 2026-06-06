import os

from flask import Flask

from routes import register_routes
from services.context_processors import registrar_context_processors
from services.decorators import proteger_rutas
from utils.filtros_fecha import registrar_filtros_fecha


def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-cambiar-en-produccion")

    register_routes(app)            # blueprints (público, privado, backoffice, auth)
    proteger_rutas(app)             # gate global de autenticación
    registrar_context_processors(app)  # curso_activo / usuario_actual en plantillas
    registrar_filtros_fecha(app)    # filtros Jinja de fecha

    return app


app = create_app()


if __name__ == "__main__":
    app.run(port=5001, debug=True)
