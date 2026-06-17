from flask import g, request, session
from utils import api_client as api

def crear_contexto_usuario(app):
    """Pasa los datos de la sesión al objeto g antes de cada request, SIN llamar a la API."""

    @app.before_request
    def cargar_usuario_desde_sesion():
        if request.endpoint == 'static' or request.path.startswith('/static/'):
            return

        g.usuario = session.get("usuario")
        g.perfiles = session.get("perfiles", [])

def guardar_usuario_actual_en_sesion():
    ok, respuesta = api.get("/auth/me")

    print("Respuesta de /auth/me:", ok, respuesta, flush=True)

    if not ok or not respuesta or not respuesta.get("usuario"):
        session.clear() # eliminamos los datos ante un problema
        return False
    
    usuario = respuesta.get("usuario")
    perfiles = respuesta.get("perfiles", [])

    session["usuario"] = usuario
    session["perfiles"] = perfiles
    g.usuario = usuario
    g.perfiles = perfiles
    return True

def get_id():
    usuario = getattr(g, "usuario", None)
    return usuario.get("id") if isinstance(usuario, dict) else None


def get_profesor_id():
    """Devuelve el id_profesor únicamente si el usuario tiene el perfil docente."""
    perfiles = get_perfiles()
    if "docente" in perfiles:
        usuario = getattr(g, "usuario", None)
        return usuario.get("profesor_id") if usuario else None
    return None


def get_alumno_id():
    """Devuelve el id_alumno únicamente si el usuario tiene el perfil alumno."""
    perfiles = get_perfiles()
    if "alumno" in perfiles:
        usuario = getattr(g, "usuario", None)
        return usuario.get("alumno_id") if usuario else None
    return None


def get_perfiles():
    """Devuelve los perfiles desde g (que se cargaron de la session)."""
    return getattr(g, "perfiles", [])

def es_staff():
    perfiles = get_perfiles()
    return "admin" in perfiles or "docente" in perfiles