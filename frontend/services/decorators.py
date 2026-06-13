from functools import wraps

from flask import flash, redirect, request, url_for

import utils.user_context as UserContext
from services.auth_service import (
    usuario_esta_logueado,
    es_staff,
    es_alumno,
)


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not usuario_esta_logueado():
            flash("Primero iniciá sesión.", "warning")
            return redirect(url_for("auth.login"))

        return view(*args, **kwargs)

    return wrapper


def requiere_staff(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not usuario_esta_logueado():
            flash("Primero iniciá sesión.", "warning")
            return redirect(url_for("auth.login"))

        perfiles = UserContext.get_perfiles()
        print(f"DEBUG perfiles: {perfiles}")   # ← agregar esta línea
        print(f"DEBUG es_staff: {es_staff(perfiles)}")  # ← y esta
        if not es_staff(perfiles):
            flash("No tenés permiso para acceder a esta sección.", "danger")
            return redirect(url_for("auth.post_login"))

        return view(*args, **kwargs)

    return wrapper


def requiere_alumno(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not usuario_esta_logueado():
            flash("Primero iniciá sesión.", "warning")
            return redirect(url_for("auth.login"))

        perfiles = UserContext.get_perfiles()

        if not es_alumno(perfiles):
            flash("No tenés permiso para acceder a esta sección.", "danger")
            return redirect(url_for("auth.post_login"))

        return view(*args, **kwargs)

    return wrapper


# ////////////////////////////////////
#  GATE GLOBAL DE AUTENTICACIÓN
# ////////////////////////////////////

# Endpoints accesibles sin sesión iniciada.
RUTAS_PUBLICAS = {
    "static",            # archivos estáticos de Flask (CSS/JS del login)
    "auth.login",        # pantalla de login (evita loop de redirección)
    "auth.logout",       # cerrar sesión debe ser siempre accesible
    "auth.finalizar_registracion",  # el profesor define su contraseña sin estar logueado
    "public.index",      # raíz (redirige a public.curso)
    "public.curso",      # home pública del curso activo
    "public.cronograma", # cronograma público
    "public.material",   # material público
    "password.solicitar_reset",   # formulario de email (sin login)
    "password.confirmar_reset",   # formulario de nueva contraseña (sin login)
}


def proteger_rutas(app):
    """Instala un guard global: toda request sin cookie de auth se
    redirige a auth.login, salvo los endpoints en RUTAS_PUBLICAS."""

    @app.before_request
    def _exigir_login():
        endpoint = request.endpoint

        # URL desconocida -> dejar que Flask devuelva 404 normalmente.
        if endpoint is None:
            return None

        # Endpoint público -> pasa sin chequear.
        if endpoint in RUTAS_PUBLICAS:
            return None

        # Usuario logueado -> pasa (los decoradores de rol siguen corriendo).
        if usuario_esta_logueado():
            return None

        # No logueado -> flash + redirect al login.
        flash("Primero iniciá sesión.", "warning")
        return redirect(url_for("auth.login"))