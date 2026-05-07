const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    let message = "No se pudo completar la solicitud";
    try {
      const body = await response.json();
      message = body.detail || message;
    } catch {
      message = response.statusText || message;
    }
    throw new Error(Array.isArray(message) ? message.map((item) => item.msg).join(", ") : message);
  }

  if (response.status === 204) return null;
  return response.json();
}

export const api = {
  baseUrl: API_URL,
  getResumen: () => request("/resumen/"),
  getPropietarios: () => request("/propietarios/?limit=500"),
  getVehiculos: () => request("/vehiculos/?limit=500"),
  getTarjetas: () => request("/tarjetas/?limit=500"),
  getUsuarios: () => request("/usuarios/?limit=500"),
  getHistorial: () => request("/historial/?limit=100"),
  getAlertas: () => request("/alertas/?limit=100"),
  getCatalogo: (name, params = "") => request(`/catalogos/${name}/${params}`),
  createPropietario: (payload) => request("/propietarios/", { method: "POST", body: JSON.stringify(payload) }),
  updatePropietario: (id, payload) => request(`/propietarios/${id}`, { method: "PATCH", body: JSON.stringify(payload) }),
  deletePropietario: (id) => request(`/propietarios/${id}`, { method: "DELETE" }),
  createVehiculo: (payload) => request("/vehiculos/", { method: "POST", body: JSON.stringify(payload) }),
  updateVehiculo: (id, payload) => request(`/vehiculos/${id}`, { method: "PATCH", body: JSON.stringify(payload) }),
  deleteVehiculo: (id) => request(`/vehiculos/${id}`, { method: "DELETE" }),
  createTarjeta: (payload) => request("/tarjetas/", { method: "POST", body: JSON.stringify(payload) }),
  updateTarjeta: (id, payload) => request(`/tarjetas/${id}`, { method: "PATCH", body: JSON.stringify(payload) }),
  deleteTarjeta: (id) => request(`/tarjetas/${id}`, { method: "DELETE" }),
  cambioPropietario: (tarjetaId, propietarioId) =>
    request(`/tarjetas/${tarjetaId}/cambio-propietario`, {
      method: "PATCH",
      body: JSON.stringify({ nuevo_propietario_id: propietarioId }),
    }),
  cambioMotor: (vehiculoId, motor) =>
    request(`/vehiculos/${vehiculoId}/cambio-motor`, {
      method: "PATCH",
      body: JSON.stringify({ nuevo_motor: motor }),
    }),
  cambioColor: (vehiculoId, colorId) =>
    request(`/vehiculos/${vehiculoId}/cambio-color`, {
      method: "PATCH",
      body: JSON.stringify({ nuevo_color_id: colorId }),
    }),
  desactivarTarjeta: (tarjetaId, estado, motivo) =>
    request(`/tarjetas/${tarjetaId}/desactivar`, {
      method: "PATCH",
      body: JSON.stringify({ nuevo_estado: estado, motivo }),
    }),
  reactivarTarjeta: (tarjetaId, motivo) =>
    request(`/tarjetas/${tarjetaId}/reactivar`, {
      method: "PATCH",
      body: JSON.stringify({ motivo }),
    }),
};
