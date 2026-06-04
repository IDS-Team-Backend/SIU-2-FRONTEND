from utils.api_client import api_request


def obtener_integrantes(equipo_id):
    ok, data = api_request(
        "GET",
        "/equipo_integrantes",
        params={"equipo_id": equipo_id}
    )

    if not ok:
        error_msg = (
            data.get("error", "Error al obtener integrantes.")
            if data else "Error de conexión."
        )
        return False, error_msg

    if not data:
        return True, []

    return True, data.get("integrantes", [])


def agregar_integrante(equipo_id, estudiante_id):
    parametros = {
        "equipo_id": equipo_id,
        "alumno_id": estudiante_id,
    }

    ok, data = api_request(
        "POST",
        "/equipo_integrantes",
        json_body=parametros
    )

    if not ok:
        error_msg = (
            data.get("error", "Error al agregar integrante.")
            if data else "Error de conexión."
        )
        return False, error_msg

    return True, data

def eliminar_integrante(equipo_id, estudiante_id):
    ok, data = api_request(
        "DELETE",
        f"/equipo_integrantes/{equipo_id}/{estudiante_id}"
    )

    if not ok:
        error_msg = (
            data.get("error", "Error al eliminar integrante.")
            if data else "Error de conexión."
        )
        return False, error_msg

    return True, None