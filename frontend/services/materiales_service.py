from utils.api_client import api_request


def obtener_materiales_del_curso(curso_id):
    ok, data = api_request("GET", "/materiales/", params={"curso_id": curso_id})
    if not ok:
        return False, data.get("error", "Error al obtener materiales")
    return True, data.get("materiales", []) if data else []


def crear_material(curso_id, titulo, archivo_url, subido_por=None):
    body = {
        "curso_id":    curso_id,
        "titulo":      titulo,
        "archivo_url": archivo_url,
    }
    if subido_por:
        body["subido_por"] = subido_por

    ok, data = api_request("POST", "/materiales/", json_body=body)
    if not ok:
        return False, data.get("error", "Error al crear el material")
    return True, data


def eliminar_material(material_id):
    ok, data = api_request("DELETE", f"/materiales/{material_id}")
    if not ok:
        return False, data.get("error", "Error al eliminar el material")
    return True, None