from flask import request, url_for

# ── Único lugar donde se declaran los filtros de la lista de alumnos y su default ──
FILTROS_ALUMNOS = {
    "page": 1,
    "estado_filtro": "",
    "sort": "apellido",
    "dir": "asc",
    "q": "",
    "eliminados": "",
}


def leer_filtros():
    """Lee del request los valores actuales de los filtros (con su default si no vienen).
    Lo usa la vista para su lógica: page, estado_filtro, q, sort, dir."""
    valores = {}
    for nombre, default in FILTROS_ALUMNOS.items():
        if isinstance(default, int):
            valores[nombre] = request.args.get(nombre, default, type=int)
        else:
            valores[nombre] = (request.args.get(nombre, default) or "").strip()
    return valores


def url_con_filtros(endpoint, **cambios):
    """Como url_for(endpoint, ...) pero arrastrando los filtros activos de la lista.
    - Los `cambios` explícitos pisan al filtro actual (ej: sort=col, page=n).
    - Los filtros que quedan en su valor por defecto se omiten → URL limpia."""
    params = {**leer_filtros(), **cambios}
    params = {
        k: v for k, v in params.items()
        if k not in FILTROS_ALUMNOS or v != FILTROS_ALUMNOS[k]
    }
    return url_for(endpoint, **params)
