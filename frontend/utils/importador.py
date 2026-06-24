import requests as req_lib

from utils.api_client import BACKEND_URL, armar_cookies_backend


def importar_lote_csv(archivo, endpoint, data=None):
    """Sube un CSV al backend para una carga masiva y normaliza la respuesta.

    POST multipart a {BACKEND_URL}{endpoint} con el archivo bajo la clave 'archivo'
    (el backend siempre lee request.files['archivo']) y `data` como campos de form
    extra (p. ej. curso_id / evaluacion_id, que no viajan dentro del CSV).

    Devuelve (True, {exitosos, duplicados, errores, detalles}) o (False, mensaje).
    Reutilizable por cualquier entidad: sólo cambian `endpoint` y `data`.
    """
    try:
        resp = req_lib.post(
            f"{BACKEND_URL}{endpoint}",
            files={"archivo": (archivo.filename, archivo.stream, "text/csv")},
            data=data or {},
            cookies=armar_cookies_backend(),
            timeout=30,
        )
        resp.raise_for_status()

        resultado = resp.json().get("resultado", {})
        return True, {
            "exitosos":   resultado.get("procesados_exito",     0),
            "duplicados": resultado.get("ignorados_duplicados", 0),
            "errores":    resultado.get("errores_encontrados",  0),
            "detalles":   resultado.get("detalles_errores",     []),
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
