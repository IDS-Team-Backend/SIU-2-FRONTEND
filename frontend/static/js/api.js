// Capa común de llamadas AJAX al backend del frontend.
// Centraliza headers (X-Requested-With) y credenciales para todos los consumidores.

// POST con cuerpo x-www-form-urlencoded. Omite las claves con valor null/undefined.
export function post(url, data = {}) {
  const body = new URLSearchParams();
  Object.keys(data).forEach((k) => {
    if (data[k] != null) body.set(k, data[k]);
  });
  return fetch(url, {
    method: "POST",
    body,
    headers: { "X-Requested-With": "fetch" },
    credentials: "same-origin",
  });
}

// GET simple que devuelve la respuesta cruda (el caller decide .text()/.json()).
export function get(url) {
  return fetch(url, {
    headers: { "X-Requested-With": "fetch" },
    credentials: "same-origin",
  });
}
