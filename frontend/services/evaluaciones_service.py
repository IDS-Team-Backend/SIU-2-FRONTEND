from utils import api_client as api


def obtener_evaluaciones_del_curso(curso_id):
    ok, data = api.get("/evaluaciones/", params={"curso_id": curso_id})

    if not ok:
        error_msg = data.get("error", "Error al obtener evaluaciones.") if data else "Error de conexión."
        return False, error_msg

    evaluaciones = data.get("evaluaciones", []) if data else []
    return True, evaluaciones

def crear_evaluacion(titulo, tipo_evaluacion_id, fecha, descripcion, curso_id):
    if not titulo or not titulo.strip():
        return False, "El título es obligatorio."

    if not tipo_evaluacion_id:
        return False, "Debes seleccionar un tipo de evaluación."

    if not fecha or not fecha.strip():
        return False, "La fecha es obligatoria."

    if not curso_id:
        return False, "Falta el ID del curso."

    parametros = {
        "titulo": titulo.strip(),
        "tipo_evaluacion_id": int(tipo_evaluacion_id),
        "fecha": fecha.strip(),
        "curso_id": int(curso_id),
    }

    if descripcion and descripcion.strip():
        parametros["descripcion"] = descripcion.strip()

    ok, data = api.post("/evaluaciones", json=parametros)

    if not ok:
        error_msg = data.get("error", "Error al crear evaluación.") if data else "Error de conexión."
        return False, error_msg

    return True, data

def actualizar_evaluacion(evaluacion_id, titulo, tipo_evaluacion_id, fecha, descripcion, curso_id):
    if not evaluacion_id:
        return False, "Falta el ID de la evaluación."
    if not titulo or not titulo.strip():
        return False, "El título es obligatorio."
    if not tipo_evaluacion_id:
        return False, "Debes seleccionar un tipo de evaluación."
    if not fecha or not fecha.strip():
        return False, "La fecha es obligatoria."

    parametros = {
        "titulo": titulo.strip(),
        "tipo_evaluacion_id": int(tipo_evaluacion_id),
        "fecha": fecha.strip(),
        "curso_id": int(curso_id),
    }

    if descripcion and descripcion.strip():
        parametros["descripcion"] = descripcion.strip()

    ok, data = api.put(f"/evaluaciones/{evaluacion_id}", json=parametros)

    if not ok:
        error_msg = data.get("error", "Error al actualizar evaluación.") if data else "Error de conexión."
        return False, error_msg

    return True, data

def eliminar_evaluacion(evaluacion_id):
    if not evaluacion_id:
        return False, "Falta el ID de la evaluación."

    ok, data = api.delete(f"/evaluaciones/{evaluacion_id}")

    if not ok:
        if data and data.get("status_code") == 404:
            return False, "La evaluación no existe o ya fue eliminada."
        error_msg = data.get("error", "Error al eliminar evaluación.") if data else "Error de conexión."
        return False, error_msg

    return True, None
