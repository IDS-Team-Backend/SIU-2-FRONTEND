from flask import request

from utils.api_client import api_request, TOKEN_COOKIE_NAME


def validar_formulario_login(form):
    errores = []

    dni_raw = form.get("dni") or form.get("username")
    password = form.get("password")

    dni = None

    if not dni_raw:
        errores.append("El DNI es obligatorio.")
    else:
        try:
            dni = int(dni_raw)
        except ValueError:
            errores.append("El DNI debe contener solo números.")

    if not password:
        errores.append("La contraseña es obligatoria.")

    return errores, dni, password


def login_backend(dni, password):
    ok, data = api_request(
        "POST",
        "/auth/login",
        json_body={
            "dni": dni,
            "password": password,
        },
        auth=False,
    )

    if not ok:
        if isinstance(data, dict):
            return False, data.get("error", "No se pudo iniciar sesión.")
        return False, "No se pudo iniciar sesión."

    if not isinstance(data, dict):
        return False, "Respuesta inválida del backend."

    token = data.get("token")

    if not token:
        return False, "El backend no devolvió token de sesión."

    return True, token


def guardar_token_en_cookie(response, token):
    response.set_cookie(
        TOKEN_COOKIE_NAME,
        token,
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=60 * 60 * 8,
    )

    return response


def borrar_token_cookie(response):
    response.delete_cookie(TOKEN_COOKIE_NAME)
    return response

#////////////////////////////////////
#  PERFILE, PERMISOS Y AUTENTICACIÓN
#////////////////////////////////////////

def usuario_logueado():
    return bool(request.cookies.get(TOKEN_COOKIE_NAME))


def obtener_perfiles_usuario():
    ok, data = api_request("GET", "/auth/me/perfiles")

    if not ok:
        return []

    if not isinstance(data, dict):
        return []

    return data.get("perfiles", [])

def es_staff(perfiles):
    return (
        "admin" in perfiles
        or "docente" in perfiles
        or "profesor" in perfiles
    )


def es_alumno(perfiles):
    return "alumno" in perfiles


def obtener_destino_por_perfil(perfiles):
    """
    Admin, docente y profesor tienen los mismos privilegios.
    Por eso van al panel staff.
    """

    if es_staff(perfiles):
        return "staff.inicio"

    if es_alumno(perfiles):
        return "alumno.inicio"

    return None