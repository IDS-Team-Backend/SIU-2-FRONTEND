from routes.auth_routes import auth_bp
from routes.alumnos_routes import alumnos_bp
from routes.materiales_routes import materiales_bp
from routes.evaluaciones_routes import evaluaciones_bp
from routes.reportes_routes import reportes_bp
from routes.perfil_routes import perfil_bp
from routes.equipos_routes import equipos_bp 
from routes.tipos_evaluaciones_router import tipo_evaluaciones_bp


def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(alumnos_bp)
    app.register_blueprint(materiales_bp)
    app.register_blueprint(evaluaciones_bp)
    app.register_blueprint(reportes_bp)
    app.register_blueprint(perfil_bp)
    app.register_blueprint(equipos_bp) 
    app.register_blueprint(tipo_evaluaciones_bp)
