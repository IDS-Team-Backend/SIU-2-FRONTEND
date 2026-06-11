import requests as req_lib
from utils.api_client import api_request, BACKEND_URL, armar_cookies_backend
import secrets
import string
ESTADOS_VALIDOS = ("activo", "abandono")



def _password_inutilizable():
    """64 caracteres random — nadie la conoce, el alumno no puede loguearse."""
    return ''.join(secrets.choice(string.ascii_letters + string.digits + "!@#$") 
                   for _ in range(64))

def obtener_alumnos_del_curso(curso_id, page=1, page_size=8, estado=None):
    """Retorna (ok, alumnos, paginacion) donde paginacion es un dict con page/total_paginas/total."""
    params = {"curso_id": curso_id, "page": page, "page_size": page_size}
    if estado:
        params["estado"] = estado

    ok_cu, data_cu = api_request("GET", "/estudiante_curso/", params=params)
    if not ok_cu:
        return False, data_cu.get("error", "Error al obtener inscripciones."), {}

    paginacion = {
        "page":          data_cu.get("page",          1) if data_cu else 1,
        "page_size":     data_cu.get("page_size",     page_size) if data_cu else page_size,
        "total":         data_cu.get("total",         0) if data_cu else 0,
        "total_paginas": data_cu.get("total_paginas", 1) if data_cu else 1,
    }

    inscripciones = data_cu.get("estudiante_cursos", []) if data_cu else []

    # el JOIN del backend ya trae todos los campos; no hace falta una segunda llamada
    resultado = [
        {
            "inscripcion_id": ins["id"],
            "estudiante_id":  ins.get("estudiante_id"),
            "usuario_id":     ins.get("usuario_id"),   
            "curso_id":       ins.get("curso_id"),
            "estado":         ins.get("estado", "activo"),
            "activo":         ins.get("estado") == "activo",
            "id":             ins.get("estudiante_id"),
            "padron":         ins.get("padron",       "—"),
            "nombre":         ins.get("nombre",       "—"),
            "apellido":       ins.get("apellido",     "—"),
            "email":          ins.get("email",        "—"),
            "dni":            ins.get("dni",          "—"),
            "carrera":        ins.get("carrera",      "—"),
            "anio_ingreso":   ins.get("anio_ingreso"),
        }
        for ins in inscripciones
    ]

    return True, resultado, paginacion


def crear_alumno(nombre, apellido, email, dni, padron, carrera, anio_ingreso):
    """
    Alta de un nuevo estudiante (sin inscribirlo al curso):
      1. POST /usuarios/   → crea la cuenta
      2. POST /estudiantes/ → crea el perfil académico
    El admin luego lo vincula al curso con el flujo de vincular.
    """
    # Crear usuario 
    password = _password_inutilizable()  # no se usa, el alumno no puede loguearse hasta que se vincule al curso
    ok_u, data_u = api_request("POST", "/usuarios/", json_body={
        "nombre":   nombre.strip(),
        "apellido": apellido.strip(),
        "email":    email.strip(),
        "dni":      int(str(dni).strip()),
        "password": password,
    })
    if not ok_u:
        errors = data_u.get("errors", []) if data_u else []
        msg = "; ".join(e.get("description", e.get("message", "")) for e in errors) if errors \
              else data_u.get("error", "Error al crear el usuario.") if data_u else "Error de conexión."
        return False, msg

    usuario_id = (data_u.get("usuario") or {}).get("id") or data_u.get("id")
    if not usuario_id:
        return False, "No se pudo obtener el ID del usuario creado."

    # Crear estudiante 
    ok_e, data_e = api_request("POST", "/estudiantes/", json_body={
        "usuario_id":   usuario_id,
        "padron":       int(padron),
        "carrera":      carrera.strip(),
        "anio_ingreso": int(anio_ingreso),
    })
    if not ok_e:
        errors = data_e.get("errors", []) if data_e else []
        msg = "; ".join(e.get("description", e.get("message", "")) for e in errors) if errors \
              else data_e.get("error", "Error al crear el estudiante.") if data_e else "Error de conexión."
        return False, msg

    return True, None


def editar_alumno(estudiante_id, usuario_id, nombre, apellido, email, dni,
                  padron, carrera, anio_ingreso):
    """
    Edita los datos personales y académicos de un alumno.
    Backend Rework/softDelete:
      - PUT /usuarios/{id}    → nombre, apellido, email, dni, activo (sin password)
      - PATCH /estudiantes/{id} → padron, carrera, anio_ingreso
    """
    errores = []

    # softDelete: PUT acepta {nombre, apellido, email, dni, activo} sin password
    if usuario_id:
        try:
            dni_int = int(str(dni).strip())
        except (ValueError, TypeError):
            return False, "El DNI debe ser un número de 8 dígitos."

        ok_u, data_u = api_request("PUT", f"/usuarios/{usuario_id}", json_body={
            "nombre":   nombre.strip(),
            "apellido": apellido.strip(),
            "email":    email.strip(),
            "dni":      dni_int,
            "activo":   True,    #  ya está en el service, verificar que esté
        })
        if not ok_u:
            msg = data_u.get("error", "Error al actualizar datos personales.") if data_u \
                  else "Error de conexión al actualizar usuario."
            errores.append(msg)
    else:
        errores.append("No se pudo identificar el usuario — datos personales no actualizados.")

    # Datos académicos via PATCH /estudiantes/{id} 
    est_body = {}
    if padron:
        try:
            est_body["padron"] = int(padron)
        except ValueError:
            errores.append("El padrón debe ser un número.")
    if carrera:
        est_body["carrera"] = carrera.strip()
    if anio_ingreso:
        try:
            est_body["anio_ingreso"] = int(anio_ingreso)
        except ValueError:
            errores.append("El año de ingreso debe ser un número.")

    if est_body:
        ok_e, data_e = api_request("PATCH", f"/estudiantes/{estudiante_id}",
                                   json_body=est_body)
        if not ok_e:
            e_list = data_e.get("errors", []) if data_e else []
            msg = "; ".join(e.get("description", e.get("message", "")) for e in e_list) if e_list \
                  else data_e.get("error", "Error al actualizar datos académicos.") if data_e \
                  else "Error de conexión al actualizar estudiante."
            errores.append(msg)

    if errores:
        return False, " | ".join(errores)
    return True, None

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


def vincular_alumno_a_curso(estudiante_id, curso_id):
    if not estudiante_id:
        return False, "Faltó el ID del alumno."
    if not curso_id:
        return False, "Faltó el ID del curso."

    ok, data = api_request("POST", "/estudiante_curso/", json_body={
        "estudiante_id": estudiante_id,
        "curso_id":      curso_id,
        "estado":        "activo",
    })

    if not ok:
        error = data.get("error", "") if data else ""
        if "ya está inscripto" in error:
            return False, "Este alumno ya está inscripto en el curso."
        return False, error or "Error al vincular alumno."

    return True, data


def desvincular_alumno_del_curso(inscripcion_id):
    ok, data = api_request("DELETE", f"/estudiante_curso/{inscripcion_id}")

    if not ok:
        if data and data.get("status_code") == 404:
            return False, "La inscripción no existe o ya fue eliminada."
        return False, data.get("error", "Error al desvincular.") if data else "Error de conexión."

    return True, None


def cambiar_estado_inscripcion(inscripcion_id, estudiante_id, curso_id, nuevo_estado):
    if nuevo_estado not in ESTADOS_VALIDOS:
        return False, f"Estado inválido: '{nuevo_estado}'. Debe ser: {', '.join(ESTADOS_VALIDOS)}."

    if not estudiante_id or not curso_id:
        return False, "Faltan datos obligatorios para actualizar el estado."
    ok, data = api_request("PUT", f"/estudiante_curso/{inscripcion_id}", json_body={
        "estudiante_id": estudiante_id,
        "curso_id":      curso_id,
        "estado":        nuevo_estado,
    })
    if not ok:
        return False, data.get("error", "Error al cambiar estado.") if data else "Error de conexión."

    return True, None


def importar_csv(archivo, curso_id):
    try:
        resp = req_lib.post(
            f"{BACKEND_URL}/estudiante_curso/importar-lote",
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