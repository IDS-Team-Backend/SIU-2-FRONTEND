from utils import api_client as api
from utils.importador import importar_lote_csv


def obtener_equipos(curso_id, evaluacion_id=None):
    params = {"curso_id": curso_id}

    if evaluacion_id:
        params["evaluacion_id"] = evaluacion_id

    ok, data = api.get(
        "/equipos",
        params=params
    )

    if not ok:
        error_msg = (
            data.get("error", "Error al obtener equipos.")
            if data else "Error de conexión."
        )
        return False, error_msg
    
    if data is None:
        return True, []
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

    ok, data = api.post(
        "/equipos",
        json=parametros
    )

    if not ok:
        error_msg = (
            data.get("error", "Error al crear equipo.")
            if data else
            "Error de conexión."
        )
        return False, error_msg

    return True, data


def actualizar_equipo(curso_id, equipo_id, evaluacion_id, nombre):
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
        "evaluacion_id": int(evaluacion_id),

    }

    ok, data = api.put(f"/equipos/{equipo_id}", json=parametros)

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

    ok, data = api.delete(
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


def importar_equipos_csv(archivo, curso_id, evaluacion_id):
    """Carga masiva de equipos. curso_id y evaluacion_id van como data del multipart
    (no en el CSV). Devuelve (ok, {exitosos, duplicados, errores, detalles}) o (False, msg)."""
    return importar_lote_csv(
        archivo,
        "/equipos/bulk",
        data={"curso_id": curso_id, "evaluacion_id": evaluacion_id},
    )