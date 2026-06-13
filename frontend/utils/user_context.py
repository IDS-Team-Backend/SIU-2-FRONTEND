from flask import g, request
from utils.api_client import api_request, TOKEN_COOKIE_NAME

def crear_contexto_usuario(app):
    """Carga datos del usuario logueado en g.usuario y g.perfiles antes de cada request."""

    @app.before_request
    def guardar_sesion_del_usuario():
        # Solo intentar si hay cookie de sesión — evita spam de warnings en páginas públicas.
        if not request.cookies.get(TOKEN_COOKIE_NAME):
            return

        ok, respuesta = api_request("GET", "/auth/me")
        if ok and respuesta:
            g.usuario = respuesta.get("usuario", {})
            g.perfiles = respuesta.get("perfiles", [])


def get_id():
    usuario = getattr(g, "usuario", None)
    if isinstance(usuario, dict):
        return usuario.get("id")
    return None

def get_profesor_id():
    """ Devuelve el id_profesor unicamente si el usuario tiene el perfil docente, sino devuelve None """
    perfiles = get_perfiles()
    if "docente" in perfiles:
            usuario = getattr(g, "usuario", None)
            if usuario:
                return usuario.get("profesor_id")
    return None

def get_alumno_id():
    """ Devuelve el id_alumno unicamente si el usuario tiene el perfil alumno, sino devuelve None """
    perfiles = get_perfiles()
    if "alumno" in perfiles:
            usuario = getattr(g, "usuario", None)
            if usuario:
                return usuario.get("alumno_id")
    return None


def get_perfiles():
    if hasattr(g, "perfiles") and g.perfiles is not None: # si los perfiles estan guardados en el contexto de usuario, los devuelve sin hacer la consulta al backend
        return g.perfiles

    ok, data = api_request("GET", "/auth/me/perfiles")

    if not ok:
        return []

    if not isinstance(data, dict):
        return []

    return data.get("perfiles", [])