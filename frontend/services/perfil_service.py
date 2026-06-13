from datetime import date, datetime
from utils.api_client import api_request
from utils.filtros_fecha import formatear_fecha as _formatear_fechafrom utils.filtros_fecha import FORMATO_BACKEND



def obtener_perfil_estudiante(curso_id):
    ok, estudiante = api_request("GET", "/estudiantes/me")
    if not ok:
        if estudiante and estudiante.get("status_code") == 404:
            return False, "Estudiante no encontrado."
        return False, estudiante.get("error", "Error al obtener perfil de estudiante.") if estudiante else "Error de conexión."


    # datos curso
    ok_curso, curso = api_request("GET", f"/cursos/{curso_id}")
    if not ok_curso:
        if curso and curso.get("status_code") == 404:
            return False, "Curso del estudiante no encontrado."
        return False, curso.get("error", "Error al obtener datos del curso.") if curso else "Error de conexión."
    curso = curso if ok_curso and curso else {}

    #datos asistencia
    ok_asistencia, asistencia = api_request("GET", f"/asistencia/cursos/{curso_id}/me")
    asistencia = asistencia if ok_asistencia and asistencia else {}

    #datos evaluaciones
    ok_evaluacion, data_evaluacion = api_request("GET", "/evaluaciones/", params={"curso_id": curso_id})
    evaluaciones_curso = data_evaluacion.get("evaluaciones", []) if ok_evaluacion and data_evaluacion else []

    #notas alumnos
    ok_notas, data_notas = api_request("GET", "/notas/", params={"alumno_id": estudiante["id"]})
    notas_lista = data_notas.get("notas", []) if ok_notas and data_notas else []
    notas_por_eval = {n["evaluacion_id"]: n.get("nota") for n in notas_lista}
 
    #promedio
    notas_valores = []
    for v in notas_por_eval.values():
        if v is not None:
            try:
                notas_valores.append(float(v))
            except (ValueError, TypeError):
                pass
    promedio = round(sum(notas_valores) / len(notas_valores), 2) if notas_valores else None

    #estado en el curso
    ok_estado, estado_data = api_request("GET", f"/curso_usuarios/",
    params={"curso_id": curso_id, "usuario_id": estudiante["usuario_id"]})
    estado_cursada = "Activo"
    if ok_estado and estado_data:
        registros = estado_data.get("curso_usuarios", [])
        if registros:
            estado_cursada = registros[0].get("estado", "activo").capitalize()
    
    #armar lista evaluaciones con notas
    evaluaciones_con_nota = []
    for ev in evaluaciones_curso:
        nota_raw = notas_por_eval.get(ev["id"])
        nota = float(nota_raw) if nota_raw is not None else None
        evaluaciones_con_nota.append({
            "titulo":  ev.get("titulo", "—"),
            "tipo":    ev.get("tipo_evaluacion", "—"),
            "fecha":   _formatear_fecha(ev.get("fecha")),
            "nota":    nota,
            "estado":  "Aprobada"     if nota is not None and nota >= 4
                    else "Desaprobada" if nota is not None
                    else "Pendiente",
        })

    #porcentaje asistencia
    porcentaje = asistencia.get("porcentaje_asistencia", "—")
    asistencia_str = (f"{porcentaje}%" if isinstance(porcentaje, (int, float))
                      else str(porcentaje))


    perfil = {
        "nombre": estudiante.get("nombre", "—"),
        "apellido": estudiante.get("apellido", "—"),
        "email": estudiante.get("email", "—"),
        "dni": estudiante.get("dni", "—"),
        "legajo": estudiante.get("padron", "—"),
        #estado cursada
        "estado_cursada": estado_cursada,
        "asistencia": asistencia_str,
        "promedio_curso": str(promedio) if promedio is not None else "Sin notas",
        #datos del curso
        "curso": {
            "codigo": curso.get("codigo", "—"),
            "nombre": curso.get("nombre", "—"),
            "carrera": curso.get("carrera", "—"),
            "comision":  curso.get("cuatrimestre", "—"),
            "modalidad": curso.get("modalidad", "—"),
            "inicio":    str(curso.get("anio", "—")),
        },
        "evaluaciones": evaluaciones_con_nota,
    }

    return True, perfil


def obtener_perfil_profesor(curso_id):
    ok, profesor = api_request("GET", "/profesores/me")
    if not ok:
        if profesor and profesor.get("status_code") == 404:
            return False, "Tu usuario no tiene un perfil de docente asociado."
        return False, profesor.get("error", "Error al cargar perfil.") if profesor else "Error de conexión."
 
    #Datos del curso (cátedra)
    ok_c, curso = api_request("GET", f"/cursos/{curso_id}")
    curso = curso if ok_c and curso else {}
 
    #Cantidad de alumnos inscriptos
    ok_cu, data_cu = api_request("GET", "/curso_usuarios/",
                                  params={"curso_id": curso_id})
    total_alumnos = data_cu.get("total", 0) if ok_cu and data_cu else 0
 
    #Calcular antigüedad desde fecha_ingreso (el backend la serializa en RFC 1123)
    antiguedad = "—"
    fecha_ingreso = profesor.get("fecha_ingreso")
    if fecha_ingreso:
        try:
            ingreso = datetime.strptime(str(fecha_ingreso), FORMATO_BACKEND).date()
            anios = max(0, date.today().year - ingreso.year)
            antiguedad = f"{anios} año{'s' if anios != 1 else ''}"
        except (ValueError, TypeError):
            antiguedad = str(fecha_ingreso)
 
    # contruir perfil
    perfil = {
        # Datos personales
        "nombre":       profesor.get("nombre", "—"),
        "apellido":     profesor.get("apellido", "—"),
        "dni":          profesor.get("dni", "—"),
        "email":        profesor.get("email", "—"),
        "rol":          profesor.get("titulo", "Docente"),
        "departamento": profesor.get("departamento", "—"),
        "fecha_ingreso": fecha_ingreso,
        "antiguedad":   antiguedad,
        # Cátedra
        "catedra": {
            "codigo":         curso.get("codigo", f"ID-{curso_id}"),
            "nombre":         curso.get("nombre", "—"),
            "rol":            "Docente",
            "modalidad":      curso.get("modalidad", "—"),
            "carga_horaria":  curso.get("horas_semanales", "—"),
            "alumnos":        total_alumnos,
        },
    }
 
    return True, perfil
 



