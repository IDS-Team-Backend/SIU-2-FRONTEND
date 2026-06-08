from routes.public_routes import public_bp
from routes.auth_routes import auth_bp
from routes.private_routes import private_bp
from routes.perfil_routes import perfil_bp
from routes.alumnos_routes import alumnos_bp
from routes.evaluaciones_routes import evaluaciones_bp
from routes.tipos_evaluaciones_router import tipo_evaluaciones_bp
from routes.equipos_routes import equipos_bp
from routes.reportes_routes import reportes_bp

# Prefijo del backoffice. 
ADMIN_PREFIX = "/admin"

# Sin prefijo: acceso + páginas públicas (no van bajo /admin).
#   - public_bp: landing + cronograma (sin login)
#   - auth_bp:   login / logout / post-login 
BLUEPRINTS_PUBLICOS = (
    public_bp,
    auth_bp,
)

# Backoffice: todo lo que se consulta autenticado vive bajo ADMIN_PREFIX.
BLUEPRINTS_BACKOFFICE = (
    private_bp,             # curso, materias, material
    perfil_bp,             # perfil del usuario
    alumnos_bp,
    evaluaciones_bp,
    tipo_evaluaciones_bp,
    equipos_bp,
    reportes_bp,
)


def register_routes(app):
    for bp in BLUEPRINTS_PUBLICOS:
        app.register_blueprint(bp)
    for bp in BLUEPRINTS_BACKOFFICE:
        app.register_blueprint(bp, url_prefix=ADMIN_PREFIX)
