import { useState, useEffect } from "react";

interface Alert {
  id: number;
  ticker: string;
  condition: "above" | "below";
  value: number;
  active: boolean;
}

const STORAGE_KEY = "alerts-data";

function loadAlerts(): Alert[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch { /* ignore */ }
  return [];
}

function saveAlerts(alerts: Alert[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(alerts));
}

export default function Alerts() {
  const [alerts, setAlerts] = useState<Alert[]>(loadAlerts);
  const [ticker, setTicker] = useState("");
  const [condition, setCondition] = useState<"above" | "below">("above");
  const [value, setValue] = useState("");

  useEffect(() => {
    saveAlerts(alerts);
  }, [alerts]);

  function addAlert() {
    if (!ticker.trim() || !value) return;
    setAlerts((prev) => [
      ...prev,
      {
        id: Date.now(),
        ticker: ticker.toUpperCase(),
        condition,
        value: Number(value),
        active: true,
      },
    ]);
    setTicker("");
    setValue("");
  }

  function toggleAlert(id: number) {
    setAlerts((prev) =>
      prev.map((a) => (a.id === id ? { ...a, active: !a.active } : a))
    );
  }

  function deleteAlert(id: number) {
    setAlerts((prev) => prev.filter((a) => a.id !== id));
  }

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-slate-800">Alertes</h1>

      {/* Add alert form */}
      <div className="rounded-xl bg-white p-5 shadow-sm">
        <h2 className="mb-4 text-sm font-semibold text-slate-800">
          Nouvelle alerte
        </h2>
        <div className="flex flex-wrap items-end gap-3">
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">
              Symbole
            </label>
            <input
              type="text"
              value={ticker}
              onChange={(e) => setTicker(e.target.value.toUpperCase())}
              placeholder="AAPL"
              className="w-32 rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">
              Condition
            </label>
            <select
              value={condition}
              onChange={(e) => setCondition(e.target.value as "above" | "below")}
              className="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-primary"
            >
              <option value="above">Au-dessus de</option>
              <option value="below">En-dessous de</option>
            </select>
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">
              Prix ($)
            </label>
            <input
              type="number"
              value={value}
              onChange={(e) => setValue(e.target.value)}
              placeholder="150.00"
              className="w-28 rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary"
            />
          </div>
          <button
            onClick={addAlert}
            className="rounded-lg bg-primary px-5 py-2 text-sm font-semibold text-white transition-colors hover:bg-primary-light"
          >
            Ajouter
          </button>
        </div>
      </div>

      {/* Alerts list */}
      <div className="rounded-xl bg-white shadow-sm">
        <div className="border-b border-slate-100 px-5 py-4">
          <h2 className="text-sm font-semibold text-slate-800">
            Alertes configurees ({alerts.length})
          </h2>
        </div>
        {alerts.length === 0 ? (
          <div className="px-5 py-12 text-center text-sm text-slate-400">
            Aucune alerte configuree
          </div>
        ) : (
          <div className="divide-y divide-slate-50">
            {alerts.map((alert) => (
              <div
                key={alert.id}
                className={`flex items-center justify-between px-5 py-4 ${
                  !alert.active ? "opacity-50" : ""
                }`}
              >
                <div className="flex items-center gap-4">
                  {/* Toggle */}
                  <button
                    onClick={() => toggleAlert(alert.id)}
                    className={`relative h-6 w-11 rounded-full transition-colors ${
                      alert.active ? "bg-primary" : "bg-slate-200"
                    }`}
                  >
                    <span
                      className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-all ${
                        alert.active ? "left-[22px]" : "left-0.5"
                      }`}
                    />
                  </button>

                  <div>
                    <span className="text-sm font-bold text-slate-800">
                      {alert.ticker}
                    </span>
                    <span className="ml-2 text-sm text-slate-500">
                      {alert.condition === "above"
                        ? "au-dessus de"
                        : "en-dessous de"}{" "}
                      <span className="font-semibold text-slate-700">
                        ${alert.value.toFixed(2)}
                      </span>
                    </span>
                  </div>
                </div>

                <button
                  onClick={() => deleteAlert(alert.id)}
                  className="rounded-lg p-2 text-slate-400 transition-colors hover:bg-slate-100 hover:text-danger"
                >
                  <svg
                    className="h-4 w-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={2}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="text-center text-xs text-slate-400">
        Les alertes sont stockees localement. Les notifications seront
        disponibles dans une prochaine version.
      </div>
    </div>
  );
}
