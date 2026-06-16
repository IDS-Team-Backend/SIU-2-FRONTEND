from utils import api_client as api


def _parse_nota(valor):
    try:
        return float(str(valor).replace(",", "."))
    except (ValueError, TypeError):
        return valor


def _notas_por(evaluacion_id, clave):
    """Devuelve {valor_de_clave: nota} para las notas de la evaluación."""
    ok, data = api.get(
        "/notas/",
        params={"evaluacion_id": evaluacion_id}
    )

    if not ok:
        error_msg = (
            data.get("error", "Error al obtener notas.")
            if data else "Error de conexión."
        )
        return False, error_msg

    notas = data.get("notas", []) if data else []

    por_sujeto = {
        nota[clave]: nota
        for nota in notas
        if nota.get(clave) is not None
    }

    return True, por_sujeto


def obtener_notas_por_equipo(evaluacion_id):
    return _notas_por(evaluacion_id, "equipo_id")


def obtener_notas_por_alumno(evaluacion_id):
    return _notas_por(evaluacion_id, "alumno_id")


def crear_nota(evaluacion_id, nota, observaciones=None, equipo_id=None, alumno_id=None):
    if not evaluacion_id:
        return False, "Falta el ID de la evaluación."

    if not equipo_id and not alumno_id:
        return False, "Falta el equipo o el alumno de la nota."

    if nota is None or str(nota).strip() == "":
        return False, "La nota es obligatoria."

    parametros = {
        "evaluacion_id": int(evaluacion_id),
        "nota": _parse_nota(nota),
    }
    if equipo_id:
        parametros["equipo_id"] = int(equipo_id)
    if alumno_id:
        parametros["alumno_id"] = int(alumno_id)

    if observaciones and observaciones.strip():
        parametros["observaciones"] = observaciones.strip()

    ok, data = api.post(
        "/notas/",
        json=parametros
    )

    if not ok:
        error_msg = (
            data.get("error", "Error al cargar la nota.")
            if data else "Error de conexión."
        )
        return False, error_msg

    return True, data


def actualizar_nota(nota_id, nota, observaciones=None):
    if not nota_id:
        return False, "Falta el ID de la nota."

    if nota is None or str(nota).strip() == "":
        return False, "La nota es obligatoria."

    parametros = {"nota": _parse_nota(nota)}
    if observaciones is not None:
        parametros["observaciones"] = observaciones.strip() or None

    ok, data = api.patch(
        f"/notas/{nota_id}",
        json=parametros
    )

    if not ok:
        error_msg = (
            data.get("error", "Error al actualizar la nota.")
            if data else "Error de conexión."
        )
        return False, error_msg

    return True, data


def eliminar_nota(nota_id):
    if not nota_id:
        return False, "Falta el ID de la nota."

    ok, data = api.delete(
        f"/notas/{nota_id}"
    )

    if not ok:
        if data and data.get("status_code") == 404:
            return False, "La nota no existe o ya fue eliminada."
        error_msg = (
            data.get("error", "Error al eliminar la nota.")
            if data else "Error de conexión."
        )
        return False, error_msg

    return True, None
