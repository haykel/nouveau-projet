import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getStock, StockQuote } from "../services/api";

const ALL_TICKERS: Record<string, string[]> = {
  Tech: ["AAPL", "MSFT", "GOOGL", "NVDA", "META", "ADBE", "CRM", "ORCL", "AMD", "INTC"],
  Finance: ["JPM", "BAC", "GS", "MS", "V", "MA"],
  "E-commerce": ["AMZN", "SHOP", "PYPL", "SQ"],
  Streaming: ["NFLX", "SPOT", "SNAP"],
  Mobilite: ["TSLA", "UBER", "LYFT"],
  Autres: ["COIN", "PLTR", "ZM", "DOCU"],
};

const SECTORS = Object.keys(ALL_TICKERS);

type SortKey = "symbol" | "current_price" | "change_percent" | "volume";

export default function Screener() {
  const navigate = useNavigate();
  const [sector, setSector] = useState("Tous");
  const [minChange, setMinChange] = useState("");
  const [maxChange, setMaxChange] = useState("");
  const [sortBy, setSortBy] = useState<SortKey>("change_percent");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");
  const [stocks, setStocks] = useState<StockQuote[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const tickers =
      sector === "Tous"
        ? Object.values(ALL_TICKERS).flat()
        : ALL_TICKERS[sector] || [];

    setLoading(true);
    Promise.all(tickers.map((t) => getStock(t).catch(() => null)))
      .then((results) => setStocks(results.filter(Boolean) as StockQuote[]))
      .finally(() => setLoading(false));
  }, [sector]);

  const filtered = stocks.filter((s) => {
    const pct = s.change_percent ?? 0;
    if (minChange !== "" && pct < Number(minChange)) return false;
    if (maxChange !== "" && pct > Number(maxChange)) return false;
    return true;
  });

  const sorted = [...filtered].sort((a, b) => {
    let va: number, vb: number;
    switch (sortBy) {
      case "symbol":
        return sortDir === "asc"
          ? a.symbol.localeCompare(b.symbol)
          : b.symbol.localeCompare(a.symbol);
      case "current_price":
        va = a.current_price;
        vb = b.current_price;
        break;
      case "change_percent":
        va = a.change_percent ?? 0;
        vb = b.change_percent ?? 0;
        break;
      case "volume":
        va = a.volume ?? 0;
        vb = b.volume ?? 0;
        break;
      default:
        return 0;
    }
    return sortDir === "asc" ? va - vb : vb - va;
  });

  function toggleSort(key: SortKey) {
    if (sortBy === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortBy(key);
      setSortDir("desc");
    }
  }

  function SortIcon({ col }: { col: SortKey }) {
    if (sortBy !== col) return null;
    return (
      <span className="ml-1 text-primary">
        {sortDir === "asc" ? "\u25B2" : "\u25BC"}
      </span>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-slate-800">Screener</h1>

      {/* Filters */}
      <div className="flex flex-wrap items-end gap-4 rounded-xl bg-white p-5 shadow-sm">
        <div>
          <label className="mb-1 block text-xs font-medium text-slate-400">
            Secteur
          </label>
          <select
            value={sector}
            onChange={(e) => setSector(e.target.value)}
            className="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-primary"
          >
            <option value="Tous">Tous les secteurs</option>
            {SECTORS.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-slate-400">
            Variation min (%)
          </label>
          <input
            type="number"
            value={minChange}
            onChange={(e) => setMinChange(e.target.value)}
            placeholder="-10"
            className="w-24 rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-primary"
          />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-slate-400">
            Variation max (%)
          </label>
          <input
            type="number"
            value={maxChange}
            onChange={(e) => setMaxChange(e.target.value)}
            placeholder="10"
            className="w-24 rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-primary"
          />
        </div>
        <div className="text-xs text-slate-400">
          {sorted.length} resultats
        </div>
      </div>

      {/* Results table */}
      {loading ? (
        <div className="text-sm text-slate-400">Chargement...</div>
      ) : (
        <div className="overflow-hidden rounded-xl bg-white shadow-sm">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-100 text-left text-xs font-medium text-slate-400">
                <th
                  className="cursor-pointer px-5 py-3 hover:text-slate-600"
                  onClick={() => toggleSort("symbol")}
                >
                  Symbole
                  <SortIcon col="symbol" />
                </th>
                <th
                  className="cursor-pointer px-5 py-3 text-right hover:text-slate-600"
                  onClick={() => toggleSort("current_price")}
                >
                  Prix
                  <SortIcon col="current_price" />
                </th>
                <th
                  className="cursor-pointer px-5 py-3 text-right hover:text-slate-600"
                  onClick={() => toggleSort("change_percent")}
                >
                  Variation
                  <SortIcon col="change_percent" />
                </th>
                <th
                  className="hidden cursor-pointer px-5 py-3 text-right hover:text-slate-600 sm:table-cell"
                  onClick={() => toggleSort("volume")}
                >
                  Volume
                  <SortIcon col="volume" />
                </th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((stock) => {
                const isPositive = (stock.change_percent ?? 0) >= 0;
                return (
                  <tr
                    key={stock.symbol}
                    onClick={() => navigate(`/stock/${stock.symbol}`)}
                    className="cursor-pointer border-b border-slate-50 transition-colors last:border-none hover:bg-slate-50"
                  >
                    <td className="px-5 py-3 text-sm font-bold text-slate-800">
                      {stock.symbol}
                    </td>
                    <td className="px-5 py-3 text-right text-sm text-slate-600">
                      ${stock.current_price.toFixed(2)}
                    </td>
                    <td className="px-5 py-3 text-right">
                      <span
                        className={`rounded-md px-2 py-0.5 text-xs font-bold ${
                          isPositive
                            ? "bg-success/10 text-success"
                            : "bg-danger/10 text-danger"
                        }`}
                      >
                        {isPositive ? "+" : ""}
                        {stock.change_percent?.toFixed(2)}%
                      </span>
                    </td>
                    <td className="hidden px-5 py-3 text-right text-sm text-slate-500 sm:table-cell">
                      {stock.volume?.toLocaleString() ?? "-"}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          {sorted.length === 0 && (
            <div className="py-8 text-center text-sm text-slate-400">
              Aucun resultat
            </div>
          )}
        </div>
      )}
    </div>
  );
}
