from datetime import datetime

# Formato en el que el backend serializa las fechas (RFC 1123).
FORMATO_BACKEND = "%a, %d %b %Y %H:%M:%S %Z"


def formatear_fecha(fecha_str):
    """RFC 1123 -> dd/mm/aaaa (para mostrar)."""
    if not fecha_str:
        return ""
    try:
        return datetime.strptime(fecha_str, FORMATO_BACKEND).strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        return fecha_str


def fecha_input(fecha_str):
    """RFC 1123 -> aaaa-mm-dd (para <input type=date>)."""
    if not fecha_str:
        return ""
    try:
        return datetime.strptime(fecha_str, FORMATO_BACKEND).strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return fecha_str


def registrar_filtros_fecha(app):
    """Registra los filtros de fecha en el entorno Jinja de la app."""
    app.add_template_filter(formatear_fecha, "formatear_fecha")
    app.add_template_filter(fecha_input, "fecha_input")
