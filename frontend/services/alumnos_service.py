from utils.api_client import api_request
import requests as req_lib
from utils.api_client import BACKEND_URL, armar_cookies_backend


def obtener_alumnos_del_curso(CURSO_ID):

    ok_cu, data_cu = api_request("GET", f"/cursos, parametros={CURSO_ID}/alumnos")

    if not ok_cu:
        error_mensaje = data_cu.get("error", "Error desconocido al obtener los alumnos del curso.") if data_cu else "Error desconocido al obtener los alumnos del curso."
        return False, error_mensaje
 
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
            "estado":         ins.get("estado", "activo"),
            "id":             est.get("id"),
            "usuario_id":     ins["usuario_id"],
            "nombre":         est.get("nombre", "—"),
            "apellido":       est.get("apellido", "—"),
            "email":          est.get("email", "—"),
            "dni":            est.get("dni", "—"),
            "padron":         est.get("padron", "—"),
            "carrera":        est.get("carrera", "—"),
            "activo":         ins.get("estado") == "activo",
        })
    return True, resultado


def buscar_alumno_por_padron(padron):
    if not str(padron).isdigit():
        return False, "El padrón debe ser un número válido."
    
    ok, data = api_request("GET", f"/estudiantes/padron/{padron}")

    if not ok:
        status = data.get("status_code") if data else None
        if status == 404:
            return False, "No se encontró ningún alumno con ese padrón."
        else:
            error_mensaje = data.get("error", "Error desconocido al buscar el alumno por padrón.") if data else "Error desconocido al buscar el alumno por padrón."
            return False, error_mensaje
        
    return True, data

def vincular_alumno_a_curso(usuario_id, curso_id):
    if not usuario_id or not curso_id:
        return False, "Usuario ID y Curso ID son requeridos para vincular un alumno al curso."
    
    ok, data = api_request("POST", "/cursos_usuarios/", json_body={
        "usuario_id": usuario_id,
        "curso_id": curso_id,
        "estado": "activo"
    })

    if not ok:
        error_mensaje = data.get("error", "") if data else ""
        if "ya_esta_inscripto" in error_mensaje.lower():
            return False, "El alumno ya está inscrito en este curso."
        return False, error_mensaje or "Error desconocido al vincular el alumno al curso."
    
    return True, data
    
def desvincular_alumno_del_curso(inscripcion_id):
    ok, data = api_request("DELETE", f"/cursos_usuarios/{inscripcion_id}")
    if not ok:
        error_mensaje = data.get("error", "Error al desvincular el alumno del curso.") if data else "Error de conexion"
        return False, error_mensaje
    return True, None

def cambiar_estado_inscripcion(inscripcion_id, nuevo_estado):
    #se necista el registro de la inscripcion para cambiar su estado, por eso se hace un get antes del put
    ok_get, data_get = api_request("GET", "/cursos_usuarios/", params={"usuario_id": None})

    ok, data = api_request("PUT", f"/cursos_usuarios/{inscripcion_id}", json_body={
        "estado": nuevo_estado
    })
    if not ok:
        error_mensaje = data.get("error", "Error al cambiar el estado de la inscripción.") if data else "Error de conexion"
        return False, error_mensaje
    return True, data

def importar_csv(curso_id, archivo):
    
    try:
        respuesta = req_lib.post(
            f"{BACKEND_URL}/curso_usuarios/importar-lote",
            files={"archivo": (archivo.filename, archivo.stream, "text/csv")},
            data={"curso_id": curso_id},
            cookies=armar_cookies_backend(),
            timeout=30,
        )
        respuesta.raise_for_status()
        return True, respuesta.json().get("resultado", {})
    except req_lib.exceptions.HTTPError as error:
        try:
            mensaje = error.response.json().get("error", str(error))
        except Exception:
            mensaje = str(error)
        return False, mensaje
    except Exception as e:
        return False, f"No se pudo conectar con el servidor: {e}"