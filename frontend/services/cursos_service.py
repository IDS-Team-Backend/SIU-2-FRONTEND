from utils.api_client import api_request

ROL_LABELS = {"titular": "Titular", "jefe_tp": "Jefe de TP", "ayudante": "Ayudante"}

ESTADO_LABELS = {
    "abierta": "Inscripción abierta",
    "inscripcion_cerrada": "Inscripción cerrada",
    "finalizada": "Cursada finalizada",
}


def _normalizar_curso(data):
    """Mapea la respuesta enriquecida del backend al shape que esperan los templates."""
    equipo = data.get("equipo_docente", []) or []
    return {
        "id":              data.get("id"),
        "materia_id":      data.get("materia_id"),
        "materia_nombre":  data.get("materia_nombre"),
        "codigo":          data.get("codigo") or "",
        "nombre":          data.get("nombre") or "",
        "descripcion":     data.get("descripcion") or "",
        "carrera":         data.get("carrera") or "",
        "modalidad":       data.get("modalidad") or "",
        "anio":            data.get("anio"),
        "cuatrimestre":    data.get("cuatrimestre"),
        "horas_semanales": data.get("horas_semanales"),
        "estado":          data.get("estado") or "abierta",
        "estado_label":    ESTADO_LABELS.get(data.get("estado"), data.get("estado") or "—"),
        "activa":          bool(data.get("activa")),
        "profesores": [
            {
                "nombre": f"{d.get('nombre', '')} {d.get('apellido', '')}".strip(),
                "rol":    ROL_LABELS.get(d.get("rol"), d.get("rol")),
            }
            for d in equipo
        ],
        "stats": data.get("stats", {"alumnos": 0, "materiales": 0, "evaluaciones": 0}),
    }


def obtener_curso_para_vista(curso_id):
    """(ok, curso_dict) con el shape que esperan los templates de curso (admin y público).
    Lee del endpoint público enriquecido (no requiere login)."""
    ok, data = api_request("GET", f"/cursos-publico/{curso_id}", auth=False)
    if not ok or not data:
        msg = data.get("error", "No se pudo obtener el curso.") if isinstance(data, dict) else "No se pudo obtener el curso."
        return False, msg
    return True, _normalizar_curso(data)


def obtener_curso_activo():
    """(ok, curso_dict) de la cursada activa del sistema (endpoint público, sin login)."""
    ok, data = api_request("GET", "/cursos-publico/activa", auth=False)
    if not ok or not data:
        return False, "No se pudo obtener la cursada activa."
    return True, _normalizar_curso(data)


def obtener_curso_activo_id():
    """Id de la cursada activa, con fallback a 1 si no se pudo resolver."""
    ok, curso = obtener_curso_activo()
    if ok and curso.get("id"):
        return curso["id"]
    return 1


def listar_cursadas():
    """Lista de todas las cursadas (para el panel de gestión)."""
    ok, data = api_request("GET", "/cursos/", params={"page_size": 100})
    if not ok or not data:
        return []
    return data.get("cursos", [])


def activar_cursada(curso_id):
    ok, data = api_request("POST", f"/cursos/{curso_id}/activar")
    if not ok:
        return False, data.get("error", "Error al activar la cursada.") if data else "Error de conexión."
    return True, data


def crear_siguiente_cursada():
    """(ok, data|error). data trae {message, curso} con la cursada nueva."""
    ok, data = api_request("POST", "/cursos/siguiente")
    if not ok:
        return False, data.get("error", "Error al crear la siguiente cursada.") if data else "Error de conexión."
    return True, data


def actualizar_curso(curso_id, datos):
    ok, data = api_request("PUT", f"/cursos/{curso_id}", json_body=datos)
    if not ok:
        return False, data.get("error", "Error al actualizar el curso.") if data else "Error de conexión."
    return True, data


def cambiar_estado_curso(curso_id, nuevo_estado):
    ok, data = api_request("PATCH", f"/cursos/{curso_id}/estado",
                           json_body={"estado": nuevo_estado})
    if not ok:
        return False, data.get("error", "Error al cambiar el estado.") if data else "Error de conexión."
    return True, data


def obtener_materias():
    ok, data = api_request("GET", "/materias/", params={"page_size": 100})
    if not ok or not data:
        return []
    return data.get("materias", [])
