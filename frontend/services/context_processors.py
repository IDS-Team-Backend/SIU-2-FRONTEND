import re as _re
from flask import request as _request
from services.auth_service import usuario_esta_logueado
from services.cursos_service import obtener_curso_para_vista
from utils import api_client as api
import utils.user_context as UserContext

_CURSO_FALLBACK = {"id": 1, "nombre": "Sistema"}

def _curso_id_del_path():
    """Extrae el curso_id de rutas tipo /admin/curso/<id>/... sin llamadas a la API."""
    m = _re.search(r'/curso/(\d+)', _request.path)
    return int(m.group(1)) if m else None


def registrar_context_processors(app):
    """Inyecta `curso_activo`, `curso_id_contexto` y `usuario_actual` en todas las plantillas."""

    @app.context_processor
    def inject_curso_activo():
        # La cursada activa es un dato del sistema (endpoint público); el sidebar
        # del backoffice la usa para armar la navegación y el bloque de contexto.
        if not usuario_esta_logueado():
            return {
                "curso_activo": _CURSO_FALLBACK,
                "curso_id_contexto": _CURSO_FALLBACK["id"],
                "curso_contexto": _CURSO_FALLBACK,
            }
        ok, data = api.get("/cursos-publico/activa", auth=False)
        curso_activo = data if (ok and data) else _CURSO_FALLBACK
        # curso_id_contexto: el id de la cursada que se está viendo ahora (puede ser
        # distinto a la activa cuando el admin navega una cursada histórica).
        curso_id_contexto = _curso_id_del_path() or curso_activo.get("id") or _CURSO_FALLBACK["id"]
        # curso_contexto: datos completos de la cursada que se está navegando. Si es la
        # activa, reutilizamos el objeto ya cargado; si es otra, la traemos por id.
        if curso_id_contexto == curso_activo.get("id"):
            curso_contexto = curso_activo
        else:
            ok_ctx, ctx = obtener_curso_para_vista(curso_id_contexto)
            curso_contexto = ctx if ok_ctx else curso_activo
        return {
            "curso_activo": curso_activo,
            "curso_id_contexto": curso_id_contexto,
            "curso_contexto": curso_contexto,
        }

    @app.context_processor
    def inject_usuario_actual():
        if not usuario_esta_logueado():
            return {"usuario_actual": None}

        perfiles = UserContext.get_perfiles()
        return {
            "usuario_actual": {
                "perfiles": perfiles,
                "es_admin":    "admin"    in perfiles,
                "es_docente":  "docente"  in perfiles,
                "es_alumno":   "alumno"   in perfiles,
                "es_ayudante": "ayudante" in perfiles,
                "es_staff":    any(p in perfiles for p in ("admin", "docente", "ayudante")),
            }
        }