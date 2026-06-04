from utils.api_client import api_request


def obtener_equipos(curso_id, evaluacion_id=None):
    params = {
        "curso_id": curso_id
    }

    if evaluacion_id:
        params["evaluacion_id"] = evaluacion_id

    ok, data = api_request(
        "GET",
        "/equipos",
        params=params
    )

    if not ok:
        error_msg = (
            data.get("error", "Error al obtener equipos.")
            if data else "Error de conexión."
        )
        return False, error_msg

    equipos = data.get("equipos", [])

    return True, equipos


def crear_equipo(curso_id, evaluacion_id, nombre):
    if not evaluacion_id:
        return False, "Debe indicarse una evaluación."

    if not nombre or not nombre.strip():
        return False, "El nombre es obligatorio."
    
    if not curso_id:
        return False, "Falta el ID del curso."

    parametros = {
        "curso_id": int(curso_id),
        "evaluacion_id": int(evaluacion_id),
        "nombre": nombre.strip(),
        
    }

    ok, data = api_request(
        "POST",
        "/equipos",
        json_body=parametros
    )

    if not ok:
        error_msg = (
            data.get("error", "Error al crear equipo.")
            if data else
            "Error de conexión."
        )
        return False, error_msg

    return True, data


def actualizar_equipo(curso_id, equipo_id, evaluacion_id, nombre, activo):
    if not equipo_id:
        return False, "Falta el ID del equipo."

    if not nombre or not nombre.strip():
        return False, "El nombre es obligatorio."
    
    if not curso_id:
        return False, "Falta el ID del curso."
    
    if not evaluacion_id: 
        return False, "Falta el ID de la evaluacion."


    parametros = {
        "curso_id": int(curso_id),
        "nombre": nombre.strip(),
        "activo": bool(activo),
        "evaluacion_id": int(evaluacion_id),

    }

    ok, data = api_request("PUT", f"/equipos/{equipo_id}",json_body=parametros
    )

    if not ok:
        error_msg = (
            data.get("error", "Error al actualizar equipo.")
            if data else
            "Error de conexión."
        )
        return False, error_msg

    return True, data


def eliminar_equipo(equipo_id):
    if not equipo_id:
        return False, "Falta el ID del equipo."

    ok, data = api_request(
        "DELETE",
        f"/equipos/{equipo_id}"
    )

    if not ok:
        if data and data.get("status_code") == 404:
            return False, "El equipo no esta activo."

        error_msg = (
            data.get("error", "Error al eliminar equipo.")
            if data else
            "Error de conexión."
        )

        return False, error_msg

    return True, None