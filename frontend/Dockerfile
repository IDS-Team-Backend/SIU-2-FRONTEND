# Imagen de PRODUCCION del frontend (multi-stage).
# - builder: instala dependencias en un venv aislado.
# - runtime: imagen limpia, codigo copiado (sin volumen), usuario no-root.
# Corre con flask SIN debug: codigo congelado, sin reload.

# ---- builder ----
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

RUN python -m venv /opt/venv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- runtime ----
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    FLASK_APP=app.py \
    FLASK_RUN_HOST=0.0.0.0 \
    FLASK_RUN_PORT=5000 \
    FLASK_DEBUG=0

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY . .

# usuario no-root (puerto 5000 > 1024, no requiere privilegios)
RUN useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

# Chequea que el server este escuchando en 5000 (sin depender de rutas ni auth, sin curl).
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import socket; socket.create_connection(('127.0.0.1', 5000), 2).close()" || exit 1

# Produccion con el dev server de Flask pero SIN debug (FLASK_DEBUG=0): sin reload, sin debugger.
# Concurrencia via threaded (default de `flask run`).
CMD ["flask", "run"]

