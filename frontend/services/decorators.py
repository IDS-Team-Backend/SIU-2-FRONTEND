from functools import wraps

from flask import flash, redirect, url_for

from services.auth_service import (
    usuario_logueado,
    obtener_perfiles_usuario,
    es_staff,
    es_alumno,
)


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not usuario_logueado():
            flash("Primero iniciá sesión.", "warning")
            return redirect(url_for("auth.login"))

        return view(*args, **kwargs)

    return wrapper


def requiere_staff(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not usuario_logueado():
            flash("Primero iniciá sesión.", "warning")
            return redirect(url_for("auth.login"))

        perfiles = obtener_perfiles_usuario()

        if not es_staff(perfiles):
            flash("No tenés permiso para acceder a esta sección.", "danger")
            return redirect(url_for("auth.post_login"))

        return view(*args, **kwargs)

    return wrapper


def requiere_alumno(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not usuario_logueado():
            flash("Primero iniciá sesión.", "warning")
            return redirect(url_for("auth.login"))

        perfiles = obtener_perfiles_usuario()

        if not es_alumno(perfiles):
            flash("No tenés permiso para acceder a esta sección.", "danger")
            return redirect(url_for("auth.post_login"))

        return view(*args, **kwargs)

    return wrapper