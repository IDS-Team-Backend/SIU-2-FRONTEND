from utils.api_client import api_request

def obtener_alumnos_reporte(curso_id, carrera=None, anio_ingreso=None, nombre_completo=None, padron=None, evaluacion_id=None, condicion=None, nota_mayor_a=None, export=None):
    if not curso_id:
        return False, "Falta el ID del curso."
    
    params = {"curso_id": curso_id}
    if carrera: params["carrera"] = carrera
    if anio_ingreso: params["anio_ingreso"] = anio_ingreso
    if nombre_completo: params["nombre_completo"] = nombre_completo
    if padron: params["padron"] = padron
    if evaluacion_id: params["evaluacion_id"] = evaluacion_id
    if condicion: params["condicion"] = condicion
    if nota_mayor_a: params["nota_mayor_a"] = nota_mayor_a
    if export: params["export"] = export

    ok, data = api_request("GET", "/reportes/alumnos", params=params, is_binary=export)
    
    if not ok:
        error_msg = data.get("error", "Error al obtener alumnos.") if data else "Error de conexión."
        return False, error_msg
    
    if export:
        return True, data
    
    alumnos = data.get("resultados", []) if data else []
    return True, alumnos


def obtener_estadisticas_reporte(curso_id, export=None):
    if not curso_id:
        return False, "Falta el ID del curso."
    
    params = {"curso_id": curso_id}
    if export: params["export"] = export

    ok, data = api_request("GET", "/reportes/estadisticas", params=params, is_binary=export)
    
    if not ok:
        error_msg = data.get("error", "Error al obtener estadísticas.") if data else "Error de conexión."
        return False, error_msg
    
    if export:
        return True, data
    
    estadisticas = data.get("resultados", []) if data else []
    return True, estadisticas


def obtener_equipos_reporte(curso_id, export=None):
    if not curso_id:
        return False, "Falta el ID del curso."
    
    params = {"curso_id": curso_id}
    if export: params["export"] = export

    ok, data = api_request("GET", "/reportes/equipos", params=params, is_binary=export)
    
    if not ok:
        error_msg = data.get("error", "Error al obtener equipos.") if data else "Error de conexión."
        return False, error_msg
    
    if export:
        return True, data
    
    equipos = data.get("resultados", []) if data else []
    return True, equipos