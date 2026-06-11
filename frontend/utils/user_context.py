    
from flask import flash, g
from utils.api_client import api_request

def crear_contexto_usuario(app):
    """ esta funcion se ejecuta antes de cada request, y se encarga de cargar en el contexto de la app (objeto 'g' de flask temporal) los datos del usuario logueado, si es que hay uno"""

    @app.before_request
    def guardar_sesion_del_usuario():
        """ esta funcion, en caso de que el usuario este logueado, 
        obtiene sus datos y perfiles y los guarda en el contexto de la app (objeto 'g' de flask temporal)"""

        ok, respuesta = api_request("GET", "/auth/me")

        if not ok or not respuesta: 
            flash("No se pudieron obtener los datos del usuario.", "warning")
            return
        
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