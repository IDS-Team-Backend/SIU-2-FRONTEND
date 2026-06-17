# Componentes compartidos del frontend

Regla de oro: **antes de escribir markup de modal / encabezado / estado vacío /
paginador / badge, usá el componente que ya existe.** El mayor problema histórico
del frontend no fue falta de componentes sino que existían y no se usaban.

Convención de ubicación:
- **Global** (lo usan varias pantallas) → `templates/components/`
- **Local** (lo usa una sola pantalla) → `templates/<area>/<pantalla>/components/`,
  con nombre `_algo.html`, incluido con `{% include %}` (comparte el contexto).

---

## Macros (se importan con `{% import "..." as x with context %}`)

### `components/page_header.html` → `page_header(titulo, subtitulo=None)`
Encabezado de pantalla. Las acciones (botones) van en el bloque `{% call %}`.
```jinja
{% import "components/page_header.html" as ph with context %}
{% call ph.page_header('Alumnos', '12 inscriptos') %}
  <a href="..." class="btn btn-primary">Nuevo</a>
{% endcall %}
```

### `components/empty_state.html` → `empty_state(icono, mensaje, accion_url=None, accion_texto=None)`
Estado vacío (ícono + mensaje + acción opcional). Para mensajes con HTML, usar `{% call %}`.
```jinja
{% import "components/empty_state.html" as es with context %}
{{ es.empty_state('group', 'No hay alumnos todavía.') }}
```

### `components/modal.html` → `modal(titulo=None, cerrar_url=None, subtitulo=None, size='sm', padded=True)`
Modal overlay con header opcional. El cuerpo va en `{% call %}`. `size`: sm | md | lg.
```jinja
{% import "components/modal.html" as modal with context %}
{% if mostrar_modal %}
  {% call modal.modal('Vincular alumno', cerrar_url=url_for('...'), subtitulo='Buscá por padrón') %}
    <form ...>...</form>
  {% endcall %}
{% endif %}
```

### `components/estado_badge.html`
- `estado_curso_badge(estado)` — mapa estado de cursada → texto/color.
- `badge(texto, tono='soft')` — badge genérico. tono: success | danger | soft | warning.
- `badge_activa(activa, ...)` — booleano "Activa / Finalizada".

### `components/cronograma_tabla.html` → `cronograma_tabla(semanas)`
Tabla de cronograma (Semana / Teórica / Práctica) del frontend público.

### `components/calendario_tabs.html` → `calendario_tabs(curso_id, activa, anio=None, mes=None)`
Pestañas Clases / Evaluaciones del backoffice (tabs server-side: cada una enlaza a
su ruta). `activa`: `'clases'` | `'evaluaciones'`. Se pasa `anio`/`mes` para preservar
el mes visible al cambiar de pestaña.

### `admin/components/paginador.html` → `paginador(paginacion, url_pagina, unidad, ...)`
Paginador server-side. **Es el único paginador**: no reimplementar (antes había 3).

### `admin/components/_importar_csv.html` → `boton_importar_csv(action_url, ...)`
Botón de carga masiva por CSV.

---

## Módulos JS (`static/js/`, cargar con `<script type="module">`)

Sin IIFE: el scope de un módulo ya es local.

- `api.js` — `post(url, data)` / `get(url)`: capa común de fetch (headers + credenciales).
- `dropdown.js` — `setupDropdown(config)` (dropdown genérico) y `setupRowActions()`
  (menú ⋮ por fila con `<details class="row-actions">`).
- `modal.js` — modales client-side por data-attrs: `data-modal-open="id"`, `data-modal-close`.
- `toggle_dropdown.js` / `sidebar_nav.js` / `row_actions.js` — configuran lo anterior por pantalla.
