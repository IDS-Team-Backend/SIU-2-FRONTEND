from routes.auth_routes import auth_bp
from routes.alumnos_routes import alumnos_bp
from routes.materiales_routes import materiales_bp

def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(alumnos_bp)
    app.register_blueprint(materiales_bp)
