from utils.api_client import api_request


def obtener_tipos_evaluacion(curso_id):
    ok, data = api_request("GET", "/tipos_evaluacion/", params={"curso_id": curso_id})

    if not ok:
        error_msg = data.get("error", "Error al obtener tipos de evaluaciones.") if data else "Error de conexión."
        return False, error_msg

    tipos_evaluacion = data.get("tipos_evaluacion", []) if data else []
    return True, tipos_evaluacion

def crear_tipo_evaluacion(nombre, es_grupal, curso_id):
    if not nombre or not nombre.strip():
        return False, "El nombre es obligatorio."

    if not curso_id:
        return False, "Falta el ID del curso."

    parametros = {
        "nombre": nombre.strip(),
        "es_grupal": es_grupal,
        "curso_id": int(curso_id),
    }

    ok, data = api_request(
        "POST",
        "/tipos_evaluacion",
        json_body=parametros
    )

    if not ok:
        error_msg = (
            data.get("error", "Error al crear tipo de evaluación.")
            if data else
            "Error de conexión."
        )
        return False, error_msg

    return True, data

def actualizar_tipo_evaluacion(tipo_evaluacion_id,nombre,es_grupal,curso_id):
    if not tipo_evaluacion_id:
        return False, "Falta el ID del tipo de evaluación."
    if not nombre or not nombre.strip():
        return False, "El nombre es obligatorio."

    if not curso_id:
        return False, "Falta el ID del curso."

    parametros = {
        "nombre": nombre.strip(),
        "es_grupal": es_grupal,
        "curso_id": int(curso_id),
    }

    ok, data = api_request(
        "PUT",
        f"/tipos_evaluacion/{tipo_evaluacion_id}",
        json_body=parametros
    )

    if not ok:
        error_msg = (
            data.get("error", "Error al actualizar tipo de evaluación.")
            if data else
            "Error de conexión."
        )
        return False, error_msg

    return True, data

def eliminar_tipo_evaluacion(tipo_evaluacion_id):
    if not tipo_evaluacion_id:
        return False, "Falta el ID del tipo de evaluación."

    ok, data = api_request("DELETE", f"/tipos_evaluacion/{tipo_evaluacion_id}")

    if not ok:
        if data and data.get("status_code") == 404:
            return False, "El tipo de evaluación no existe o ya fue eliminado."
        if data and data.get("status_code") == 500:
            return False, "No se puede eliminar este tipo porque esta asociado a una evaluacion."
        error_msg = data.get("error", "No se pudo eliminar esta evaluacion") if data else "Error de conexión."
        return False, error_msg

    return True, None
