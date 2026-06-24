## SIU-2 FRONTEND

---

## 1. Preparar el backend

Abrir una terminal:

```bash
cd SIU-2-BACKEND
git checkout development
```

Crear entorno virtual si no existe:

```bash
python3 -m venv .venv
```

Activarlo:

```bash
source .venv/bin/activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Levantar el backend:

```bash
python app.py 5000
```

El backend debe quedar corriendo en:

```text
http://localhost:5000
```

---

## 2. Verificar que el backend esté activo

En otra terminal:

```bash
curl -i http://localhost:5000/materiales/health
```

Si responde, el backend está levantado.

---

## 3. Crear un usuario admin de prueba

El schema actual usa la columna:

```text
es_admin
```

No usa:

```text
rol_id
```

Por eso, para un admin de prueba, el usuario debe tener:

```text
es_admin = TRUE
activo = TRUE
```

---

## 4. Generar contraseña hasheada

En una terminal con el entorno del backend activado:

```bash
cd SIU-2-BACKEND
source .venv/bin/activate
python3
```

Dentro de Python:

```python
from werkzeug.security import generate_password_hash

print(generate_password_hash("admin123"))
```

Copiar el hash completo generado.

Ejemplo de contraseña para probar:

```text
admin123
```

---

## 5. Insertar el usuario en MYSQL

Abrir MYSQL y conectarse a la base de datos del backend.

Primero verificar si ya existe el usuario:

```sql
SELECT id, nombre, apellido, email, dni, es_admin, activo
FROM usuarios
WHERE dni = 99999999;
```

Si no existe, insertarlo:

```sql
INSERT INTO usuarios
(nombre, apellido, email, dni, password_hash, es_admin, activo)
VALUES
(
  'Admin',
  'Prueba',
  'admin.prueba@gmail.com',
  99999999,
  'PEGAR_HASH_ACA',
  TRUE,
  TRUE
);
```

Reemplazar:

```text
PEGAR_HASH_ACA
```

por el hash generado con Python.

---

## 6. Confirmar que el usuario quedó cargado

Ejecutar en MYSQL:

```sql
SELECT id, nombre, apellido, email, dni, es_admin, activo
FROM usuarios
WHERE dni = 99999999;
```

Debe aparecer algo así:

```text
dni = 99999999
es_admin = 1 / TRUE
activo = 1 / TRUE
```

---

## 7. Preparar el frontend

Abrir otra terminal:

```bash
cd SIU-2-FRONTEND
git checkout development
```

Crear entorno virtual si no existe:

```bash
python3 -m venv .venv
```

Activarlo:

```bash
source .venv/bin/activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

---

## 8. Crear archivo `.env` del frontend

En la raíz de `SIU-2-FRONTEND`, crear un archivo llamado:

```text
.env
```

Con este contenido:

```env
BACKEND_URL=http://localhost:5000
FRONTEND_SECRET_KEY=clave-dev-cambiar
BACKEND_TIMEOUT=10
```

---

## 9. Levantar el frontend

Desde `SIU-2-FRONTEND`:

```bash
source .venv/bin/activate
flask --app frontend.app run --port 5001 --debug
```

El frontend debe quedar corriendo en:

```text
http://localhost:5001
```
