import os
import requests
from flask import request

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000").rstrip("/")
TIMEOUT = int(os.getenv("BACKEND_TIMEOUT", "10"))
TOKEN_COOKIE_NAME = "access_token_cookie"


def obtener_token():
    return request.cookies.get(TOKEN_COOKIE_NAME)


def armar_cookies_backend():
    token = obtener_token()

    if not token:
        return None

    return {
        TOKEN_COOKIE_NAME: token
    }


def limpiar_params(params):
    if not params:
        return None

    limpios = {}

    for clave, valor in params.items():
        if valor not in (None, ""):
            limpios[clave] = valor

    return limpios


def extraer_mensaje_error(response, data):
    if isinstance(data, dict):
        # Formato actual del backend:
        # {"errors": [{"code": "...", "message": "..."}]}
        errors = data.get("errors")

        if isinstance(errors, list) and len(errors) > 0:
            primer_error = errors[0]

            if isinstance(primer_error, dict):
                return (
                    primer_error.get("message")
                    or primer_error.get("description")
                    or f"Error del backend ({response.status_code})"
                )

        # Otros formatos posibles
        return (
            data.get("error")
            or data.get("message")
            or data.get("mensaje")
            or data.get("detail")
            or f"Error del backend ({response.status_code})"
        )

    return f"Error del backend ({response.status_code})"


def api_request(method, path, params=None, json_body=None, auth=True):
    url = f"{BACKEND_URL}{path}"

    try:
        response = requests.request(
            method=method,
            url=url,
            params=limpiar_params(params),
            json=json_body,
            cookies=armar_cookies_backend() if auth else None,
            timeout=TIMEOUT,
        )
    except requests.RequestException as exc:
        return False, {
            "error": f"No se pudo conectar con el backend: {exc}"
        }

    if response.status_code == 204:
        return True, None

    try:
        data = response.json()
    except ValueError:
        data = {}

    if not response.ok:
        mensaje = extraer_mensaje_error(response, data)

        return False, {
        "error": mensaje,
        "status_code": response.status_code,
        }

    return True, data