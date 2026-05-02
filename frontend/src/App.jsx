import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  Car,
  CheckCircle2,
  CircleOff,
  ClipboardList,
  Gauge,
  History,
  LayoutDashboard,
  Menu,
  Palette,
  Plus,
  RefreshCw,
  Search,
  Settings,
  ShieldCheck,
  Trash2,
  UserRound,
  Users,
  Wrench,
  X,
} from "lucide-react";
import { api } from "./api";

const navItems = [
  { id: "tarjetas", label: "Tarjetas", icon: ClipboardList },
  { id: "propietarios", label: "Propietarios", icon: Users },
  { id: "vehiculos", label: "Vehiculos", icon: Car },
  { id: "mantenimiento", label: "Mantenimiento", icon: Wrench },
  { id: "auditoria", label: "Auditoria", icon: History },
];

const emptyCatalogs = {
  departamentos: [],
  municipios: [],
  tipos: [],
  marcas: [],
  lineas: [],
  colores: [],
};

function compactPayload(payload) {
  return Object.fromEntries(
    Object.entries(payload).map(([key, value]) => {
      if (value === "") return [key, null];
      if (key.startsWith("id_") || ["modelo_anio", "cilindros", "cilindrada_cc", "ejes", "pasajeros"].includes(key)) {
        return [key, value === null ? null : Number(value)];
      }
      if (key === "tonelaje") return [key, value === null ? null : Number(value)];
      return [key, value];
    })
  );
}

function today() {
  return new Date().toISOString().slice(0, 10);
}

function nextYear() {
  const date = new Date();
  date.setFullYear(date.getFullYear() + 1);
  return date.toISOString().slice(0, 10);
}

function fullName(owner) {
  if (!owner) return "Sin propietario";
  return [owner.primer_nombre, owner.segundo_nombre, owner.primer_apellido, owner.segundo_apellido].filter(Boolean).join(" ");
}

function formatDate(value) {
  if (!value) return "Sin fecha";
  return new Intl.DateTimeFormat("es-GT", { day: "2-digit", month: "short", year: "numeric" }).format(new Date(value));
}

function App() {
  const [activeView, setActiveView] = useState("tarjetas");
  const [data, setData] = useState({ resumen: {}, propietarios: [], vehiculos: [], tarjetas: [], usuarios: [], historial: [], alertas: [] });
  const [catalogs, setCatalogs] = useState(emptyCatalogs);
  const [query, setQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("TODOS");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [modal, setModal] = useState(null);
  const [toast, setToast] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  async function loadData() {
    setLoading(true);
    setError("");
    try {
      const [
        resumen,
        propietarios,
        vehiculos,
        tarjetas,
        usuarios,
        historial,
        alertas,
        departamentos,
        municipios,
        tipos,
        marcas,
        lineas,
        colores,
      ] = await Promise.all([
        api.getResumen(),
        api.getPropietarios(),
        api.getVehiculos(),
        api.getTarjetas(),
        api.getUsuarios(),
        api.getHistorial(),
        api.getAlertas(),
        api.getCatalogo("departamentos"),
        api.getCatalogo("municipios"),
        api.getCatalogo("tipos-vehiculo"),
        api.getCatalogo("marcas"),
        api.getCatalogo("lineas"),
        api.getCatalogo("colores"),
      ]);

      setData({ resumen, propietarios, vehiculos, tarjetas, usuarios, historial, alertas });
      setCatalogs({ departamentos, municipios, tipos, marcas, lineas, colores });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  const lookup = useMemo(() => {
    const by = (items, key) => Object.fromEntries(items.map((item) => [item[key], item]));
    return {
      propietarios: by(data.propietarios, "id_propietario"),
      vehiculos: by(data.vehiculos, "id_vehiculo"),
      tarjetas: by(data.tarjetas, "id_tarjeta"),
      usuarios: by(data.usuarios, "id_usuario"),
      municipios: by(catalogs.municipios, "id_municipio"),
      departamentos: by(catalogs.departamentos, "id_departamento"),
      tipos: by(catalogs.tipos, "id_tipo_vehiculo"),
      marcas: by(catalogs.marcas, "id_marca"),
      lineas: by(catalogs.lineas, "id_linea"),
      colores: by(catalogs.colores, "id_color"),
    };
  }, [data, catalogs]);

  const tarjetasDetalladas = useMemo(() => {
    return data.tarjetas.map((tarjeta) => {
      const vehiculo = lookup.vehiculos[tarjeta.id_vehiculo];
      const propietario = lookup.propietarios[tarjeta.id_propietario];
      return {
        ...tarjeta,
        propietario_nombre: fullName(propietario),
        dpi: propietario?.dpi || "",
        vehiculo_label: vehiculo
          ? `${lookup.marcas[vehiculo.id_marca]?.nombre || "Marca"} ${lookup.lineas[vehiculo.id_linea]?.nombre || ""}`
          : "Vehiculo no encontrado",
        placa: vehiculo?.placa || "",
        color: lookup.colores[vehiculo?.id_color]?.nombre || "",
        uso: vehiculo?.uso || "",
      };
    });
  }, [data.tarjetas, lookup]);

  const filteredRows = tarjetasDetalladas.filter((item) => {
    const text = `${item.numero_tarjeta} ${item.propietario_nombre} ${item.dpi} ${item.placa} ${item.vehiculo_label}`.toLowerCase();
    const matchesText = text.includes(query.toLowerCase());
    const matchesStatus = statusFilter === "TODOS" || item.estado === statusFilter;
    return matchesText && matchesStatus;
  });

  async function runAction(action, successMessage) {
    try {
      await action();
      setToast(successMessage);
      setModal(null);
      await loadData();
      window.setTimeout(() => setToast(""), 2600);
    } catch (err) {
      setError(err.message);
    }
  }

  const currentTitle = navItems.find((item) => item.id === activeView)?.label || "Tarjetas";

  return (
    <div className="app-shell">
      <aside className={`sidebar ${sidebarOpen ? "open" : ""}`}>
        <div className="brand">
          <div className="brand-mark">
            <ShieldCheck size={22} />
          </div>
          <div>
            <strong>Circulacion GT</strong>
            <span>Tarjetas vehiculares</span>
          </div>
        </div>

        <nav className="nav-list">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <button key={item.id} className={activeView === item.id ? "active" : ""} onClick={() => setActiveView(item.id)}>
                <Icon size={18} />
                {item.label}
              </button>
            );
          })}
        </nav>

        <div className="connection-card">
          <span>API conectada</span>
          <strong>{api.baseUrl.replace(/^https?:\/\//, "")}</strong>
        </div>
      </aside>

      <main className="workspace">
        <header className="topbar">
          <button className="icon-button mobile-only" title="Abrir navegacion" onClick={() => setSidebarOpen(!sidebarOpen)}>
            <Menu size={20} />
          </button>
          <div>
            <span className="eyebrow">Universidad Rafael Landivar</span>
            <h1>{currentTitle}</h1>
          </div>
          <div className="topbar-actions">
            <button className="ghost-button" onClick={loadData} title="Actualizar datos">
              <RefreshCw size={17} />
              Actualizar
            </button>
            {activeView !== "auditoria" && activeView !== "mantenimiento" && (
              <button className="primary-button" onClick={() => setModal({ type: activeView, mode: "create" })}>
                <Plus size={18} />
                Nuevo registro
              </button>
            )}
          </div>
        </header>

        {toast && <div className="toast">{toast}</div>}
        {error && (
          <div className="error-banner">
            <AlertTriangle size={18} />
            <span>{error}</span>
            <button className="icon-button" onClick={() => setError("")} title="Cerrar alerta">
              <X size={16} />
            </button>
          </div>
        )}

        <section className="metrics-grid">
          <Metric label="Tarjetas" value={data.resumen.total_tarjetas || 0} icon={ClipboardList} tone="blue" />
          <Metric label="Vigentes" value={data.resumen.vigentes || 0} icon={CheckCircle2} tone="green" />
          <Metric label="Vencen pronto" value={data.resumen.vencen_pronto || 0} icon={Gauge} tone="amber" />
          <Metric label="Alertas activas" value={data.resumen.alertas_activas || 0} icon={AlertTriangle} tone="red" />
        </section>

        {activeView === "tarjetas" && (
          <TarjetasView
            rows={filteredRows}
            loading={loading}
            query={query}
            setQuery={setQuery}
            statusFilter={statusFilter}
            setStatusFilter={setStatusFilter}
            onEdit={(row) => setModal({ type: "tarjetas", mode: "edit", record: row })}
            onDelete={(row) => setModal({ type: "confirm-delete-tarjeta", record: row })}
            onSuspend={(row) => setModal({ type: "desactivar", record: row })}
            onReactivate={(row) => setModal({ type: "reactivar", record: row })}
          />
        )}

        {activeView === "propietarios" && (
          <PropietariosView
            propietarios={data.propietarios}
            lookup={lookup}
            onEdit={(record) => setModal({ type: "propietarios", mode: "edit", record })}
            onDelete={(record) => setModal({ type: "confirm-delete-propietario", record })}
          />
        )}

        {activeView === "vehiculos" && (
          <VehiculosView
            vehiculos={data.vehiculos}
            lookup={lookup}
            onEdit={(record) => setModal({ type: "vehiculos", mode: "edit", record })}
            onDelete={(record) => setModal({ type: "confirm-delete-vehiculo", record })}
          />
        )}

        {activeView === "mantenimiento" && (
          <MantenimientoView
            tarjetas={tarjetasDetalladas}
            propietarios={data.propietarios}
            vehiculos={data.vehiculos}
            colores={catalogs.colores}
            onAction={runAction}
          />
        )}

        {activeView === "auditoria" && <AuditoriaView historial={data.historial} alertas={data.alertas} lookup={lookup} />}
      </main>

      {modal && (
        <AppModal title={modalTitle(modal)} onClose={() => setModal(null)}>
          {["tarjetas", "propietarios", "vehiculos"].includes(modal.type) && (
            <EntityForm
              modal={modal}
              catalogs={catalogs}
              data={data}
              nextCardNumber={nextCardNumber(data.tarjetas)}
              onSubmit={(payload) => {
                if (modal.type === "propietarios") {
                  return runAction(
                    () =>
                      modal.mode === "create"
                        ? api.createPropietario(payload)
                        : api.updatePropietario(modal.record.id_propietario, payload),
                    "Propietario guardado"
                  );
                }
                if (modal.type === "vehiculos") {
                  return runAction(
                    () =>
                      modal.mode === "create" ? api.createVehiculo(payload) : api.updateVehiculo(modal.record.id_vehiculo, payload),
                    "Vehiculo guardado"
                  );
                }
                return runAction(
                  () => (modal.mode === "create" ? api.createTarjeta(payload) : api.updateTarjeta(modal.record.id_tarjeta, payload)),
                  "Tarjeta guardada"
                );
              }}
            />
          )}

          {modal.type === "desactivar" && (
            <DeactivateForm
              record={modal.record}
              onSubmit={(payload) =>
                runAction(() => api.desactivarTarjeta(modal.record.id_tarjeta, payload.estado, payload.motivo), "Estado actualizado")
              }
            />
          )}

          {modal.type === "reactivar" && (
            <ReactivateForm
              record={modal.record}
              onSubmit={(payload) =>
                runAction(() => api.reactivarTarjeta(modal.record.id_tarjeta, payload.motivo), "Tarjeta reactivada")
              }
            />
          )}

          {modal.type.startsWith("confirm-delete") && (
            <ConfirmDelete
              label={deleteLabel(modal)}
              onCancel={() => setModal(null)}
              onConfirm={() =>
                runAction(() => {
                  if (modal.type === "confirm-delete-propietario") return api.deletePropietario(modal.record.id_propietario);
                  if (modal.type === "confirm-delete-vehiculo") return api.deleteVehiculo(modal.record.id_vehiculo);
                  return api.deleteTarjeta(modal.record.id_tarjeta);
                }, "Registro eliminado")
              }
            />
          )}
        </AppModal>
      )}
    </div>
  );
}

function Metric({ label, value, icon: Icon, tone }) {
  return (
    <article className={`metric ${tone}`}>
      <span className="metric-icon">
        <Icon size={20} />
      </span>
      <div>
        <strong>{value}</strong>
        <span>{label}</span>
      </div>
    </article>
  );
}

function TarjetasView({ rows, loading, query, setQuery, statusFilter, setStatusFilter, onEdit, onDelete, onSuspend, onReactivate }) {
  return (
    <section className="data-panel">
      <div className="panel-toolbar">
        <div className="search-box">
          <Search size={18} />
          <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Buscar por tarjeta, placa, propietario o DPI" />
        </div>
        <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
          <option value="TODOS">Todos los estados</option>
          <option value="VIGENTE">Vigente</option>
          <option value="VENCIDA">Vencida</option>
          <option value="SUSPENDIDA">Suspendida</option>
          <option value="CANCELADA">Cancelada</option>
        </select>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Tarjeta</th>
              <th>Propietario</th>
              <th>Vehiculo</th>
              <th>Estado</th>
              <th>Vencimiento</th>
              <th>Uso</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan="7" className="empty-state">Cargando informacion...</td></tr>
            ) : rows.length === 0 ? (
              <tr><td colSpan="7" className="empty-state">No hay tarjetas con esos filtros.</td></tr>
            ) : (
              rows.map((row) => (
                <tr key={row.id_tarjeta}>
                  <td>
                    <strong>{row.numero_tarjeta}</strong>
                    <span className="muted">ID {row.id_tarjeta}</span>
                  </td>
                  <td>
                    <strong>{row.propietario_nombre}</strong>
                    <span className="muted">{row.dpi}</span>
                  </td>
                  <td>
                    <strong>{row.placa}</strong>
                    <span className="muted">{row.vehiculo_label} · {row.color}</span>
                  </td>
                  <td><StatusBadge status={row.estado} /></td>
                  <td>{formatDate(row.fecha_vencimiento)}</td>
                  <td>{row.uso}</td>
                  <td className="row-actions">
                    <button className="icon-button" title="Editar tarjeta" onClick={() => onEdit(row)}><Settings size={17} /></button>
                    {row.estado === "SUSPENDIDA" ? (
                      <button className="icon-button success-action" title="Reactivar tarjeta" onClick={() => onReactivate(row)}><RefreshCw size={17} /></button>
                    ) : (
                      <button className="icon-button" title="Suspender o cancelar" onClick={() => onSuspend(row)}><CircleOff size={17} /></button>
                    )}
                    <button className="icon-button danger" title="Eliminar tarjeta" onClick={() => onDelete(row)}><Trash2 size={17} /></button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function PropietariosView({ propietarios, lookup, onEdit, onDelete }) {
  return (
    <section className="data-panel">
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Propietario</th>
              <th>DPI</th>
              <th>Municipio</th>
              <th>Contacto</th>
              <th>NIT</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {propietarios.map((owner) => (
              <tr key={owner.id_propietario}>
                <td><strong>{fullName(owner)}</strong><span className="muted">Registrado {formatDate(owner.fecha_registro)}</span></td>
                <td>{owner.dpi}</td>
                <td>{lookup.municipios[owner.id_municipio]?.nombre || "Sin municipio"}</td>
                <td><span>{owner.telefono || "Sin telefono"}</span><span className="muted">{owner.correo || "Sin correo"}</span></td>
                <td>{owner.nit || "CF"}</td>
                <td className="row-actions">
                  <button className="icon-button" title="Editar propietario" onClick={() => onEdit(owner)}><Settings size={17} /></button>
                  <button className="icon-button danger" title="Eliminar propietario" onClick={() => onDelete(owner)}><Trash2 size={17} /></button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function VehiculosView({ vehiculos, lookup, onEdit, onDelete }) {
  return (
    <section className="data-panel">
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Placa</th>
              <th>Vehiculo</th>
              <th>VIN</th>
              <th>Motor</th>
              <th>Color</th>
              <th>Uso</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {vehiculos.map((vehicle) => (
              <tr key={vehicle.id_vehiculo}>
                <td><strong>{vehicle.placa}</strong><span className="muted">Modelo {vehicle.modelo_anio}</span></td>
                <td>{lookup.marcas[vehicle.id_marca]?.nombre || "Marca"} {lookup.lineas[vehicle.id_linea]?.nombre || ""}</td>
                <td>{vehicle.vin}</td>
                <td>{vehicle.numero_motor}</td>
                <td>{lookup.colores[vehicle.id_color]?.nombre || "Sin color"}</td>
                <td>{vehicle.uso}</td>
                <td className="row-actions">
                  <button className="icon-button" title="Editar vehiculo" onClick={() => onEdit(vehicle)}><Settings size={17} /></button>
                  <button className="icon-button danger" title="Eliminar vehiculo" onClick={() => onDelete(vehicle)}><Trash2 size={17} /></button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function MantenimientoView({ tarjetas, propietarios, vehiculos, colores, onAction }) {
  const [tarjetaId, setTarjetaId] = useState(tarjetas[0]?.id_tarjeta || "");
  const selected = tarjetas.find((item) => String(item.id_tarjeta) === String(tarjetaId));
  const selectedVehicle = vehiculos.find((item) => item.id_vehiculo === selected?.id_vehiculo);
  const propietariosDisponibles = propietarios.filter((owner) => owner.id_propietario !== selected?.id_propietario);
  const coloresDisponibles = colores.filter((color) => color.id_color !== selectedVehicle?.id_color);
  const estadosDisponibles = (selected?.estado === "SUSPENDIDA"
    ? ["VIGENTE", "CANCELADA", "VENCIDA"]
    : ["SUSPENDIDA", "CANCELADA", "VENCIDA"]
  ).filter((estado) => estado !== selected?.estado);

  useEffect(() => {
    if (!tarjetaId && tarjetas[0]) setTarjetaId(tarjetas[0].id_tarjeta);
  }, [tarjetas, tarjetaId]);

  return (
    <section className="maintenance-layout">
      <div className="maintenance-summary">
        <label>Tarjeta a mantener</label>
        <select value={tarjetaId} onChange={(event) => setTarjetaId(event.target.value)}>
          {tarjetas.map((tarjeta) => (
            <option key={tarjeta.id_tarjeta} value={tarjeta.id_tarjeta}>
              {tarjeta.numero_tarjeta} · {tarjeta.placa} · {tarjeta.propietario_nombre}
            </option>
          ))}
        </select>
        {selected && (
          <div className="selected-card">
            <StatusBadge status={selected.estado} />
            <h2>{selected.numero_tarjeta}</h2>
            <p>{selected.propietario_nombre}</p>
            <p>{selected.placa} · {selected.vehiculo_label}</p>
          </div>
        )}
      </div>

      <div className="maintenance-actions">
        <MaintenanceCard
          icon={UserRound}
          title="Cambio de propietario"
          fields={
            propietariosDisponibles.length > 0 ? (
              <SelectField name="id_propietario" label="Nuevo propietario" options={propietariosDisponibles} valueKey="id_propietario" labelKey={fullName} />
            ) : (
              <p className="helper-copy">No hay otro propietario disponible para esta tarjeta.</p>
            )
          }
          onSubmit={(payload) => onAction(() => api.cambioPropietario(tarjetaId, payload.id_propietario), "Propietario actualizado")}
          disabled={propietariosDisponibles.length === 0}
        />
        <MaintenanceCard
          icon={Gauge}
          title="Cambio de motor"
          fields={<TextField name="numero_motor" label="Nuevo numero de motor" required />}
          onSubmit={(payload) => onAction(() => api.cambioMotor(selectedVehicle?.id_vehiculo, payload.numero_motor), "Motor actualizado")}
        />
        <MaintenanceCard
          icon={Palette}
          title="Cambio de color"
          fields={
            coloresDisponibles.length > 0 ? (
              <SelectField name="id_color" label="Nuevo color" options={coloresDisponibles} valueKey="id_color" labelKey="nombre" />
            ) : (
              <p className="helper-copy">No hay otro color disponible en el catalogo.</p>
            )
          }
          onSubmit={(payload) => onAction(() => api.cambioColor(selectedVehicle?.id_vehiculo, payload.id_color), "Color actualizado")}
          disabled={coloresDisponibles.length === 0}
        />
        <MaintenanceCard
          icon={CircleOff}
          title="Desactivacion"
          fields={
            <>
              <SelectField
                name="estado"
                label="Nuevo estado"
                options={estadosDisponibles}
              />
              <TextField name="motivo" label="Motivo" required />
            </>
          }
          onSubmit={(payload) => {
            const action = payload.estado === "VIGENTE"
              ? () => api.reactivarTarjeta(tarjetaId, payload.motivo)
              : () => api.desactivarTarjeta(tarjetaId, payload.estado, payload.motivo);
            onAction(action, payload.estado === "VIGENTE" ? "Tarjeta reactivada" : "Tarjeta desactivada");
          }}
        />
      </div>
    </section>
  );
}

function MaintenanceCard({ icon: Icon, title, fields, onSubmit, disabled = false }) {
  return (
    <form className="maintenance-card" onSubmit={(event) => {
      event.preventDefault();
      if (disabled) return;
      onSubmit(compactPayload(Object.fromEntries(new FormData(event.currentTarget))));
      event.currentTarget.reset();
    }}>
      <div className="card-title"><Icon size={19} /><strong>{title}</strong></div>
      {fields}
      <button className="primary-button" type="submit" disabled={disabled}>Aplicar</button>
    </form>
  );
}

function AuditoriaView({ historial, alertas, lookup }) {
  return (
    <section className="audit-grid">
      <div className="data-panel">
        <div className="panel-title"><History size={18} /> Historial de cambios</div>
        <div className="timeline">
          {historial.map((item) => (
            <article key={item.id_historial}>
              <strong>{formatAuditType(item.tipo_cambio)}</strong>
              <span>{formatAuditCard(item.id_tarjeta, lookup)} · {formatDate(item.fecha_hora)}</span>
              <p>{formatAuditValue(item.tipo_cambio, item.valor_anterior, lookup)} → {formatAuditValue(item.tipo_cambio, item.valor_nuevo, lookup)}</p>
            </article>
          ))}
        </div>
      </div>
      <div className="data-panel">
        <div className="panel-title"><AlertTriangle size={18} /> Alertas</div>
        <div className="timeline">
          {alertas.map((item) => (
            <article key={item.id_alerta}>
              <strong>{formatAuditType(item.tipo_alerta)}</strong>
              <span>{formatAuditType(item.estado_alerta)} · {formatAuditCard(item.id_tarjeta, lookup)}</span>
              <p>{item.descripcion || "Sin descripcion"}</p>
            </article>
          ))}
          {alertas.length === 0 && <p className="empty-state">No hay alertas registradas.</p>}
        </div>
      </div>
    </section>
  );
}

function formatAuditCard(tarjetaId, lookup) {
  const tarjeta = lookup.tarjetas[Number(tarjetaId)];
  if (!tarjeta) return `Tarjeta ID ${tarjetaId}`;

  const vehiculo = lookup.vehiculos[tarjeta.id_vehiculo];
  const placa = vehiculo?.placa ? ` · ${vehiculo.placa}` : "";
  return `${tarjeta.numero_tarjeta}${placa}`;
}

function formatAuditType(value) {
  return String(value || "")
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatAuditValue(type, value, lookup) {
  if (value === null || value === undefined || value === "") return "Sin valor";

  const numericId = Number(value);
  const hasNumericId = Number.isInteger(numericId);

  if (type === "PROPIETARIO" && hasNumericId) {
    const owner = lookup.propietarios[numericId];
    return owner ? `${fullName(owner)} · DPI ${owner.dpi}` : `Propietario ID ${value}`;
  }

  if (type === "COLOR" && hasNumericId) {
    const color = lookup.colores[numericId];
    return color ? color.nombre : `Color ID ${value}`;
  }

  if (type === "ESTADO") {
    return formatAuditType(value);
  }

  if (type === "MOTOR") {
    return `Motor ${value}`;
  }

  if (type === "PLACA") {
    return `Placa ${value}`;
  }

  return String(value);
}

function EntityForm({ modal, catalogs, data, nextCardNumber, onSubmit }) {
  const record = modal.record || {};
  const isEdit = modal.mode === "edit";

  function handleSubmit(event) {
    event.preventDefault();
    onSubmit(compactPayload(Object.fromEntries(new FormData(event.currentTarget))));
  }

  return (
    <form className="form-grid" onSubmit={handleSubmit}>
      {modal.type === "propietarios" && (
        <>
          <TextField name="dpi" label="DPI" defaultValue={record.dpi} required />
          <TextField name="nit" label="NIT" defaultValue={record.nit} />
          <TextField name="primer_nombre" label="Primer nombre" defaultValue={record.primer_nombre} required />
          <TextField name="segundo_nombre" label="Segundo nombre" defaultValue={record.segundo_nombre} />
          <TextField name="primer_apellido" label="Primer apellido" defaultValue={record.primer_apellido} required />
          <TextField name="segundo_apellido" label="Segundo apellido" defaultValue={record.segundo_apellido} />
          <TextField name="fecha_nacimiento" label="Fecha de nacimiento" type="date" defaultValue={record.fecha_nacimiento} required />
          <SelectField name="id_municipio" label="Municipio" options={catalogs.municipios} valueKey="id_municipio" labelKey="nombre" defaultValue={record.id_municipio} />
          <TextField name="telefono" label="Telefono" defaultValue={record.telefono} />
          <TextField name="correo" label="Correo" type="email" defaultValue={record.correo} />
          <label className="field wide"><span>Direccion</span><textarea name="direccion" defaultValue={record.direccion} required /></label>
        </>
      )}

      {modal.type === "vehiculos" && (
        <>
          <TextField name="vin" label="VIN" defaultValue={record.vin} required />
          <TextField
            name="placa"
            label="Placa"
            defaultValue={record.placa}
            required
            disabled={isEdit}
            title={isEdit ? "Campo protegido por auditoria" : undefined}
          />
          <SelectField name="id_tipo_vehiculo" label="Tipo" options={catalogs.tipos} valueKey="id_tipo_vehiculo" labelKey="nombre" defaultValue={record.id_tipo_vehiculo} />
          <SelectField name="id_marca" label="Marca" options={catalogs.marcas} valueKey="id_marca" labelKey="nombre" defaultValue={record.id_marca} />
          <SelectField name="id_linea" label="Linea" options={catalogs.lineas} valueKey="id_linea" labelKey="nombre" defaultValue={record.id_linea} />
          <SelectField
            name="id_color"
            label="Color"
            options={catalogs.colores}
            valueKey="id_color"
            labelKey="nombre"
            defaultValue={record.id_color}
            disabled={isEdit}
            title={isEdit ? "Usa Mantenimiento para registrar este cambio en auditoria" : undefined}
          />
          <TextField name="modelo_anio" label="Modelo" type="number" defaultValue={record.modelo_anio} required />
          <TextField
            name="numero_motor"
            label="Motor"
            defaultValue={record.numero_motor}
            required
            disabled={isEdit}
            title={isEdit ? "Usa Mantenimiento para registrar este cambio en auditoria" : undefined}
          />
          <TextField name="numero_chasis" label="Chasis" defaultValue={record.numero_chasis} required />
          <TextField name="cilindros" label="Cilindros" type="number" defaultValue={record.cilindros} />
          <TextField name="cilindrada_cc" label="Cilindrada cc" type="number" defaultValue={record.cilindrada_cc} />
          <TextField name="ejes" label="Ejes" type="number" defaultValue={record.ejes || 2} required />
          <TextField name="tonelaje" label="Tonelaje" type="number" step="0.01" defaultValue={record.tonelaje} />
          <TextField name="pasajeros" label="Pasajeros" type="number" defaultValue={record.pasajeros} />
          <SelectField name="combustible" label="Combustible" options={["GASOLINA", "DIESEL", "ELECTRICO", "HIBRIDO"]} defaultValue={record.combustible || "GASOLINA"} />
          <SelectField name="uso" label="Uso" options={["PARTICULAR", "COMERCIAL", "OFICIAL", "DIPLOMATICO"]} defaultValue={record.uso || "PARTICULAR"} />
        </>
      )}

      {modal.type === "tarjetas" && (
        <>
          <SelectField name="id_vehiculo" label="Vehiculo" options={data.vehiculos} valueKey="id_vehiculo" labelKey={(item) => `${item.placa} · ${item.vin}`} defaultValue={record.id_vehiculo} />
          <SelectField name="id_propietario" label="Propietario" options={data.propietarios} valueKey="id_propietario" labelKey={fullName} defaultValue={record.id_propietario} />
          <TextField name="numero_tarjeta" label="Numero de tarjeta" defaultValue={record.numero_tarjeta || nextCardNumber} required />
          <TextField name="fecha_emision" label="Emision" type="date" defaultValue={record.fecha_emision || today()} required />
          <TextField name="fecha_vencimiento" label="Vencimiento" type="date" defaultValue={record.fecha_vencimiento || nextYear()} required />
          <SelectField name="estado" label="Estado" options={["VIGENTE", "VENCIDA", "SUSPENDIDA", "CANCELADA"]} defaultValue={record.estado || "VIGENTE"} />
          <SelectField name="id_usuario_emision" label="Usuario emisor" options={data.usuarios} valueKey="id_usuario" labelKey="nombre_completo" defaultValue={record.id_usuario_emision} allowEmpty />
          <label className="field wide"><span>Observaciones</span><textarea name="observaciones" defaultValue={record.observaciones} /></label>
        </>
      )}

      <div className="form-actions">
        <button className="primary-button" type="submit">{isEdit ? "Guardar cambios" : "Crear registro"}</button>
      </div>
    </form>
  );
}

function DeactivateForm({ record, onSubmit }) {
  return (
    <form className="form-grid single" onSubmit={(event) => {
      event.preventDefault();
      onSubmit(Object.fromEntries(new FormData(event.currentTarget)));
    }}>
      <p className="modal-copy">La tarjeta {record.numero_tarjeta} cambiara de estado y se registrara una alerta si aplica.</p>
      <SelectField name="estado" label="Nuevo estado" options={["SUSPENDIDA", "CANCELADA", "VENCIDA"]} defaultValue="SUSPENDIDA" />
      <TextField name="motivo" label="Motivo" required />
      <div className="form-actions"><button className="primary-button danger-fill" type="submit">Actualizar estado</button></div>
    </form>
  );
}

function ReactivateForm({ record, onSubmit }) {
  return (
    <form className="form-grid single" onSubmit={(event) => {
      event.preventDefault();
      onSubmit(Object.fromEntries(new FormData(event.currentTarget)));
    }}>
      <p className="modal-copy">La tarjeta {record.numero_tarjeta} volvera a estado VIGENTE y sus alertas activas se marcaran como resueltas.</p>
      <TextField name="motivo" label="Motivo de reactivacion" required />
      <div className="form-actions"><button className="primary-button success-fill" type="submit">Reactivar tarjeta</button></div>
    </form>
  );
}

function ConfirmDelete({ label, onConfirm, onCancel }) {
  return (
    <div className="confirm-box">
      <p>Estas por eliminar <strong>{label}</strong>. Si tiene relaciones activas, PostgreSQL rechazara la operacion para proteger la integridad referencial.</p>
      <div className="form-actions">
        <button className="ghost-button" onClick={onCancel}>Cancelar</button>
        <button className="primary-button danger-fill" onClick={onConfirm}>Eliminar</button>
      </div>
    </div>
  );
}

function TextField({ label, ...props }) {
  return (
    <label className="field">
      <span>{label}</span>
      <input {...props} defaultValue={props.defaultValue ?? ""} />
    </label>
  );
}

function SelectField({ label, options, valueKey, labelKey, allowEmpty, ...props }) {
  return (
    <label className="field">
      <span>{label}</span>
      <select {...props} defaultValue={props.defaultValue ?? ""} required={!allowEmpty}>
        {allowEmpty && <option value="">Sin asignar</option>}
        {options.map((item) => {
          const value = typeof item === "string" ? item : item[valueKey];
          const labelText = typeof item === "string" ? item : typeof labelKey === "function" ? labelKey(item) : item[labelKey];
          return <option key={value} value={value}>{labelText}</option>;
        })}
      </select>
    </label>
  );
}

function StatusBadge({ status }) {
  return <span className={`status-badge ${String(status).toLowerCase()}`}>{status}</span>;
}

function AppModal({ title, children, onClose }) {
  return (
    <div className="modal-backdrop">
      <div className="modal">
        <div className="modal-header">
          <h2>{title}</h2>
          <button className="icon-button" title="Cerrar" onClick={onClose}><X size={18} /></button>
        </div>
        {children}
      </div>
    </div>
  );
}

function modalTitle(modal) {
  const verb = modal.mode === "edit" ? "Editar" : "Nuevo";
  if (modal.type === "tarjetas") return `${verb} tarjeta de circulacion`;
  if (modal.type === "propietarios") return `${verb} propietario`;
  if (modal.type === "vehiculos") return `${verb} vehiculo`;
  if (modal.type === "desactivar") return "Desactivar tarjeta";
  if (modal.type === "reactivar") return "Reactivar tarjeta";
  return "Confirmar eliminacion";
}

function deleteLabel(modal) {
  if (modal.type === "confirm-delete-propietario") return fullName(modal.record);
  if (modal.type === "confirm-delete-vehiculo") return modal.record.placa;
  return modal.record.numero_tarjeta;
}

function nextCardNumber(tarjetas) {
  const next = tarjetas.length + 1;
  return `TC-${new Date().getFullYear()}-${String(next).padStart(6, "0")}`;
}

export default App;
