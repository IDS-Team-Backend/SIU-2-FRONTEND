from utils.api_client import api_request


def _normalizar_fecha(valor):
    # <input type="datetime-local"> entrega "AAAA-MM-DDThh:mm";
    # MySQL DATETIME espera "AAAA-MM-DD hh:mm:ss".
    return str(valor).strip().replace("T", " ")


def _entregas_por(evaluacion_id, clave):
    """Devuelve {valor_de_clave: entrega} para las entregas de la evaluación."""
    ok, data = api_request(
        "GET",
        "/entregas/",
        params={"evaluacion_id": evaluacion_id}
    )

    if not ok:
        error_msg = (
            data.get("error", "Error al obtener entregas.")
            if data else "Error de conexión."
        )
        return False, error_msg

    entregas = data.get("entregas", []) if data else []

    por_sujeto = {
        entrega[clave]: entrega
        for entrega in entregas
        if entrega.get(clave) is not None
    }

    return True, por_sujeto


def obtener_entregas_por_equipo(evaluacion_id):
    return _entregas_por(evaluacion_id, "equipo_id")


def obtener_entregas_por_alumno(evaluacion_id):
    return _entregas_por(evaluacion_id, "alumno_id")


def crear_entrega(evaluacion_id, fecha_entrega, estado, archivo_url=None, observaciones=None,
                  equipo_id=None, alumno_id=None):
    if not evaluacion_id:
        return False, "Falta el ID de la evaluación."

    if not equipo_id and not alumno_id:
        return False, "Falta el equipo o el alumno de la entrega."

    if not fecha_entrega or not str(fecha_entrega).strip():
        return False, "La fecha de entrega es obligatoria."

    parametros = {
        "evaluacion_id": int(evaluacion_id),
        "fecha_entrega": _normalizar_fecha(fecha_entrega),
        "estado": estado or "entregado",
    }
    if equipo_id:
        parametros["equipo_id"] = int(equipo_id)
    if alumno_id:
        parametros["alumno_id"] = int(alumno_id)

    if archivo_url and archivo_url.strip():
        parametros["archivo_url"] = archivo_url.strip()

    if observaciones and observaciones.strip():
        parametros["observaciones"] = observaciones.strip()

    ok, data = api_request(
        "POST",
        "/entregas/",
        json_body=parametros
    )

    if not ok:
        error_msg = (
            data.get("error", "Error al registrar entrega.")
            if data else "Error de conexión."
        )
        return False, error_msg

    return True, data


def eliminar_entrega(entrega_id):
    if not entrega_id:
        return False, "Falta el ID de la entrega."

    ok, data = api_request(
        "DELETE",
        f"/entregas/{entrega_id}"
    )

    if not ok:
        if data and data.get("status_code") == 404:
            return False, "La entrega no existe o ya fue eliminada."
        error_msg = (
            data.get("error", "Error al eliminar entrega.")
            if data else "Error de conexión."
        )
        return False, error_msg

    return True, None
