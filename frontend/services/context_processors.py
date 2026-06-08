import os

from services.auth_service import usuario_logueado
from utils.api_client import api_request

CURSO_ACTIVO_ID = int(os.getenv("CURSO_ACTIVO_ID", "1"))

_CURSO_FALLBACK = {"id": CURSO_ACTIVO_ID, "nombre": "Sistema"}


def registrar_context_processors(app):
    """Inyecta `curso_activo` y `usuario_actual` en todas las plantillas."""

    @app.context_processor
    def inject_curso_activo():
        if not usuario_logueado():
            return {"curso_activo": _CURSO_FALLBACK}
        ok, data = api_request("GET", f"/cursos/{CURSO_ACTIVO_ID}")
        if ok and data:
            return {"curso_activo": data}
        return {"curso_activo": _CURSO_FALLBACK}

    @app.context_processor
    def inject_usuario_actual():
        if not usuario_logueado():
            return {"usuario_actual": None}
        ok, data = api_request("GET", "/auth/me/perfiles")
        if ok and data:
            return {"usuario_actual": {"perfiles": data.get("perfiles", [])}}
        return {"usuario_actual": None}
