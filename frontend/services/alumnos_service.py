import requests as req_lib
from utils.api_client import api_request, BACKEND_URL, armar_cookies_backend

ESTADOS_VALIDOS = ("activo", "suspendido", "baja")


def obtener_alumnos_del_curso(curso_id):
    ok_cu, data_cu = api_request("GET", "/curso_usuarios/",
                                 params={"curso_id": curso_id})
    if not ok_cu:
        return False, data_cu.get("error", "Error al obtener inscripciones.")

    inscripciones = data_cu.get("curso_usuarios", []) if data_cu else []
    if not inscripciones:
        return True, []

    ok_est, data_est = api_request("GET", "/estudiantes/")
    est_por_usuario = {}
    if ok_est and data_est:
        for e in data_est.get("estudiantes", []):
            est_por_usuario[e["usuario_id"]] = e

    resultado = []
    for ins in inscripciones:
        est = est_por_usuario.get(ins["usuario_id"], {})
        resultado.append({
            "inscripcion_id": ins["id"],
            "usuario_id":     ins["usuario_id"],
            "curso_id":       ins["curso_id"],
            "estado":         ins.get("estado", "activo"),
            "activo":         ins.get("estado") == "activo",
            "id":             est.get("id"),
            "padron":         est.get("padron",   "—"),
            "nombre":         est.get("nombre",   "—"),
            "apellido":       est.get("apellido", "—"),
            "email":          est.get("email",    "—"),
            "dni":            est.get("dni",      "—"),
            "carrera":        est.get("carrera",  "—"),
            "anio_ingreso":   est.get("anio_ingreso"),
        })

    return True, resultado


def buscar_alumno_por_padron(padron):
    padron = str(padron).strip()

    if not padron:
        return False, "Ingresá un padrón."

    if not padron.isdigit():
        return False, "El padrón debe contener solo números."

    ok, data = api_request("GET", f"/estudiantes/padron/{padron}")

    if not ok:
        if data and data.get("status_code") == 404:
            return False, f"No se encontró ningún alumno con padrón {padron}."
        return False, data.get("error", "Error al buscar alumno.") if data else "Error de conexión."

    return True, data


def vincular_alumno_a_curso(usuario_id, curso_id):
    if not usuario_id:
        return False, "Faltó el ID del alumno."
    if not curso_id:
        return False, "Faltó el ID del curso."

    ok, data = api_request("POST", "/curso_usuarios/", json_body={
        "usuario_id": usuario_id,
        "curso_id":   curso_id,
        "estado":     "activo",
    })

    if not ok:
        error = data.get("error", "") if data else ""
        if "ya está inscripto" in error:
            return False, "Este alumno ya está inscripto en el curso."
        return False, error or "Error al vincular alumno."

    return True, data


def desvincular_alumno_del_curso(inscripcion_id):
    ok, data = api_request("DELETE", f"/curso_usuarios/{inscripcion_id}")

    if not ok:
        if data and data.get("status_code") == 404:
            return False, "La inscripción no existe o ya fue eliminada."
        return False, data.get("error", "Error al desvincular.") if data else "Error de conexión."

    return True, None


def cambiar_estado_inscripcion(inscripcion_id, usuario_id, curso_id, nuevo_estado):
    if nuevo_estado not in ESTADOS_VALIDOS:
        return False, f"Estado inválido: '{nuevo_estado}'. Debe ser: {', '.join(ESTADOS_VALIDOS)}."

    if not usuario_id or not curso_id:
        return False, "Faltan datos obligatorios para actualizar el estado."

    ok, data = api_request("PUT", f"/curso_usuarios/{inscripcion_id}",
                           json_body={
                               "usuario_id": usuario_id,
                               "curso_id":   curso_id,
                               "estado":     nuevo_estado,
                           })

    if not ok:
        return False, data.get("error", "Error al cambiar estado.") if data else "Error de conexión."

    registro = data.get("curso", data)
    return True, registro


def importar_csv(archivo, curso_id):
    try:
        resp = req_lib.post(
            f"{BACKEND_URL}/curso_usuarios/importar-lote",
            files={"archivo": (archivo.filename, archivo.stream, "text/csv")},
            data={"curso_id": curso_id},
            cookies=armar_cookies_backend(),
            timeout=30,
        )
        resp.raise_for_status()

        data = resp.json()
        resultado_raw = data.get("resultado", {})

        return True, {
            "exitosos":   resultado_raw.get("procesados_exito",    0),
            "duplicados": resultado_raw.get("ignorados_duplicados", 0),
            "errores":    resultado_raw.get("errores_encontrados",  0),
            "detalles":   resultado_raw.get("detalles_errores",     []),
        }

    except req_lib.exceptions.HTTPError as e:
        try:
            errores = e.response.json().get("errors", [])
            msg = errores[0].get("message", str(e)) if errores else str(e)
        except Exception:
            msg = str(e)
        return False, msg

    except req_lib.exceptions.ConnectionError:
        return False, "No se pudo conectar con el servidor."

    except Exception as e:
        return False, f"Error inesperado: {e}"