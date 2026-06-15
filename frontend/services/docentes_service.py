from utils import api_client as api

ROLES_PARTICIPACION = ("titular", "jefe_tp", "ayudante")


def obtener_equipo_docente(curso_id):
    """Retorna (ok, integrantes) — integrantes es lista, o string de error si ok=False."""
    ok, data = api.get("/curso_docentes/", params={"curso_id": curso_id})
    if not ok:
        return False, data.get("error", "Error al obtener el equipo docente.") if data else "Error de conexión."

    integrantes = data.get("integrantes", []) if data else []
    return True, integrantes


def agregar_docente(curso_id, docente_id, rol):
    if not docente_id:
        return False, "Faltó seleccionar el profesor."
    if rol not in ROLES_PARTICIPACION:
        return False, f"Tipo de participación inválido: '{rol}'."

    ok, data = api.post("/curso_docentes/", json={
        "curso_id":   curso_id,
        "docente_id": docente_id,
        "nombre":     rol,
    })
    if not ok:
        return False, data.get("error", "Error al agregar integrante.") if data else "Error de conexión."
    return True, data


def cambiar_participacion(integrante_id, rol):
    if rol not in ROLES_PARTICIPACION:
        return False, f"Tipo de participación inválido: '{rol}'."

    ok, data = api.patch(f"/curso_docentes/{integrante_id}",
                           json={"nombre": rol})
    if not ok:
        return False, data.get("error", "Error al cambiar la participación.") if data else "Error de conexión."
    return True, None


def quitar_docente(integrante_id):
    ok, data = api.delete(f"/curso_docentes/{integrante_id}")
    if not ok:
        if data and data.get("status_code") == 404:
            return False, "El integrante no existe o ya fue eliminado."
        return False, data.get("error", "Error al quitar integrante.") if data else "Error de conexión."
    return True, None
