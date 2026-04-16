import { useState, useEffect, useRef } from "react";
import { createChart, IChartApi, LineData } from "lightweight-charts";
import { getStock, StockQuote } from "../services/api";

interface Position {
  symbol: string;
  shares: number;
  avgPrice: number;
}

interface Transaction {
  id: number;
  type: "BUY" | "SELL";
  symbol: string;
  shares: number;
  price: number;
  date: string;
}

const INITIAL_CAPITAL = 10000;
const STORAGE_KEY = "portfolio-data";

function loadState(): { positions: Position[]; transactions: Transaction[]; cash: number } {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch { /* ignore */ }
  return { positions: [], transactions: [], cash: INITIAL_CAPITAL };
}

function saveState(state: { positions: Position[]; transactions: Transaction[]; cash: number }) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

export default function Portfolio() {
  const [state, setState] = useState(loadState);
  const [prices, setPrices] = useState<Record<string, number>>({});
  const [ticker, setTicker] = useState("");
  const [shares, setShares] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const chartRef = useRef<HTMLDivElement>(null);
  const chartApiRef = useRef<IChartApi | null>(null);

  useEffect(() => {
    saveState(state);
  }, [state]);

  // Fetch live prices for positions
  useEffect(() => {
    if (state.positions.length === 0) return;
    Promise.all(
      state.positions.map((p) =>
        getStock(p.symbol)
          .then((q: StockQuote) => [p.symbol, q.current_price] as const)
          .catch(() => [p.symbol, 0] as const)
      )
    ).then((results) => {
      const map: Record<string, number> = {};
      for (const [sym, price] of results) map[sym] = price;
      setPrices(map);
    });
  }, [state.positions]);

  // Performance chart
  useEffect(() => {
    if (!chartRef.current || state.transactions.length === 0) return;

    if (chartApiRef.current) {
      chartApiRef.current.remove();
      chartApiRef.current = null;
    }

    const chart = createChart(chartRef.current, {
      width: chartRef.current.clientWidth,
      height: 200,
      layout: { background: { color: "#ffffff" }, textColor: "#94a3b8" },
      grid: { vertLines: { color: "#f1f5f9" }, horzLines: { color: "#f1f5f9" } },
      rightPriceScale: { borderColor: "#e2e8f0" },
      timeScale: { borderColor: "#e2e8f0" },
    });
    chartApiRef.current = chart;

    const series = chart.addLineSeries({ color: "#4f46e5", lineWidth: 2 });
    let balance = INITIAL_CAPITAL;
    const data: LineData[] = [];
    for (const tx of state.transactions) {
      if (tx.type === "BUY") balance -= tx.price * tx.shares;
      else balance += tx.price * tx.shares;
      data.push({ time: tx.date, value: balance });
    }
    series.setData(data);
    chart.timeScale().fitContent();

    const handleResize = () => {
      if (chartRef.current && chartApiRef.current)
        chartApiRef.current.applyOptions({ width: chartRef.current.clientWidth });
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
      chartApiRef.current = null;
    };
  }, [state.transactions]);

  const totalValue = state.positions.reduce(
    (sum, p) => sum + p.shares * (prices[p.symbol] || p.avgPrice),
    0
  );
  const portfolioValue = state.cash + totalValue;
  const pnl = portfolioValue - INITIAL_CAPITAL;
  const pnlPct = (pnl / INITIAL_CAPITAL) * 100;

  async function handleTrade(type: "BUY" | "SELL") {
    if (!ticker.trim() || shares <= 0) return;
    setLoading(true);
    setError(null);

    try {
      const quote = await getStock(ticker.toUpperCase());
      const price = quote.current_price;
      const cost = price * shares;

      if (type === "BUY") {
        if (cost > state.cash) {
          setError("Fonds insuffisants");
          setLoading(false);
          return;
        }
        const existing = state.positions.find((p) => p.symbol === quote.symbol);
        const newPositions = existing
          ? state.positions.map((p) =>
              p.symbol === quote.symbol
                ? {
                    ...p,
                    shares: p.shares + shares,
                    avgPrice:
                      (p.avgPrice * p.shares + price * shares) /
                      (p.shares + shares),
                  }
                : p
            )
          : [...state.positions, { symbol: quote.symbol, shares, avgPrice: price }];

        setState((s) => ({
          ...s,
          cash: s.cash - cost,
          positions: newPositions,
          transactions: [
            ...s.transactions,
            {
              id: Date.now(),
              type: "BUY",
              symbol: quote.symbol,
              shares,
              price,
              date: new Date().toISOString().split("T")[0],
            },
          ],
        }));
      } else {
        const existing = state.positions.find((p) => p.symbol === quote.symbol);
        if (!existing || existing.shares < shares) {
          setError("Actions insuffisantes");
          setLoading(false);
          return;
        }
        const remaining = existing.shares - shares;
        const newPositions =
          remaining === 0
            ? state.positions.filter((p) => p.symbol !== quote.symbol)
            : state.positions.map((p) =>
                p.symbol === quote.symbol ? { ...p, shares: remaining } : p
              );

        setState((s) => ({
          ...s,
          cash: s.cash + cost,
          positions: newPositions,
          transactions: [
            ...s.transactions,
            {
              id: Date.now(),
              type: "SELL",
              symbol: quote.symbol,
              shares,
              price,
              date: new Date().toISOString().split("T")[0],
            },
          ],
        }));
      }
      setTicker("");
      setShares(1);
    } catch {
      setError("Impossible de recuperer le prix");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-slate-800">Portfolio</h1>

      {/* Summary cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="rounded-xl bg-white p-5 shadow-sm">
          <div className="mb-1 text-xs font-medium text-slate-400">
            Valeur du portefeuille
          </div>
          <div className="text-2xl font-bold text-slate-800">
            ${portfolioValue.toFixed(2)}
          </div>
        </div>
        <div className="rounded-xl bg-white p-5 shadow-sm">
          <div className="mb-1 text-xs font-medium text-slate-400">
            Cash disponible
          </div>
          <div className="text-2xl font-bold text-slate-800">
            ${state.cash.toFixed(2)}
          </div>
        </div>
        <div className="rounded-xl bg-white p-5 shadow-sm">
          <div className="mb-1 text-xs font-medium text-slate-400">
            P&L total
          </div>
          <div
            className={`text-2xl font-bold ${
              pnl >= 0 ? "text-success" : "text-danger"
            }`}
          >
            {pnl >= 0 ? "+" : ""}${pnl.toFixed(2)}
            <span className="ml-2 text-sm">
              ({pnlPct >= 0 ? "+" : ""}
              {pnlPct.toFixed(2)}%)
            </span>
          </div>
        </div>
      </div>

      {/* Performance chart */}
      {state.transactions.length > 0 && (
        <div className="rounded-xl bg-white p-5 shadow-sm">
          <h2 className="mb-3 text-sm font-semibold text-slate-800">
            Performance
          </h2>
          <div ref={chartRef} className="w-full overflow-hidden rounded-lg" />
        </div>
      )}

      {/* Trade form */}
      <div className="rounded-xl bg-white p-5 shadow-sm">
        <h2 className="mb-4 text-sm font-semibold text-slate-800">
          Passer un ordre
        </h2>
        <div className="flex flex-wrap items-end gap-3">
          <div>
            <label className="mb-1 block text-xs text-slate-400">Symbole</label>
            <input
              type="text"
              value={ticker}
              onChange={(e) => setTicker(e.target.value.toUpperCase())}
              placeholder="AAPL"
              className="w-32 rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs text-slate-400">Quantite</label>
            <input
              type="number"
              min={1}
              value={shares}
              onChange={(e) => setShares(Math.max(1, Number(e.target.value)))}
              className="w-24 rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary"
            />
          </div>
          <button
            onClick={() => handleTrade("BUY")}
            disabled={loading}
            className="rounded-lg bg-success px-5 py-2 text-sm font-semibold text-white transition-colors hover:bg-green-600 disabled:opacity-50"
          >
            Acheter
          </button>
          <button
            onClick={() => handleTrade("SELL")}
            disabled={loading}
            className="rounded-lg bg-danger px-5 py-2 text-sm font-semibold text-white transition-colors hover:bg-red-600 disabled:opacity-50"
          >
            Vendre
          </button>
        </div>
        {error && (
          <div className="mt-2 text-sm text-danger">{error}</div>
        )}
      </div>

      {/* Positions */}
      <div className="rounded-xl bg-white shadow-sm">
        <div className="border-b border-slate-100 px-5 py-4">
          <h2 className="text-sm font-semibold text-slate-800">Positions</h2>
        </div>
        {state.positions.length === 0 ? (
          <div className="px-5 py-8 text-center text-sm text-slate-400">
            Aucune position
          </div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-100 text-left text-xs font-medium text-slate-400">
                <th className="px-5 py-2.5">Symbole</th>
                <th className="px-5 py-2.5 text-right">Quantite</th>
                <th className="px-5 py-2.5 text-right">PRU</th>
                <th className="px-5 py-2.5 text-right">Prix actuel</th>
                <th className="px-5 py-2.5 text-right">P&L</th>
              </tr>
            </thead>
            <tbody>
              {state.positions.map((p) => {
                const currentPrice = prices[p.symbol] || p.avgPrice;
                const positionPnl = (currentPrice - p.avgPrice) * p.shares;
                const positionPnlPct = ((currentPrice - p.avgPrice) / p.avgPrice) * 100;
                return (
                  <tr
                    key={p.symbol}
                    className="border-b border-slate-50 last:border-none"
                  >
                    <td className="px-5 py-3 text-sm font-bold text-slate-800">
                      {p.symbol}
                    </td>
                    <td className="px-5 py-3 text-right text-sm text-slate-600">
                      {p.shares}
                    </td>
                    <td className="px-5 py-3 text-right text-sm text-slate-600">
                      ${p.avgPrice.toFixed(2)}
                    </td>
                    <td className="px-5 py-3 text-right text-sm text-slate-600">
                      ${currentPrice.toFixed(2)}
                    </td>
                    <td className="px-5 py-3 text-right">
                      <span
                        className={`text-sm font-semibold ${
                          positionPnl >= 0 ? "text-success" : "text-danger"
                        }`}
                      >
                        {positionPnl >= 0 ? "+" : ""}${positionPnl.toFixed(2)}
                        <span className="ml-1 text-xs">
                          ({positionPnlPct >= 0 ? "+" : ""}
                          {positionPnlPct.toFixed(1)}%)
                        </span>
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Transaction history */}
      <div className="rounded-xl bg-white shadow-sm">
        <div className="border-b border-slate-100 px-5 py-4">
          <h2 className="text-sm font-semibold text-slate-800">
            Historique des transactions
          </h2>
        </div>
        {state.transactions.length === 0 ? (
          <div className="px-5 py-8 text-center text-sm text-slate-400">
            Aucune transaction
          </div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-100 text-left text-xs font-medium text-slate-400">
                <th className="px-5 py-2.5">Date</th>
                <th className="px-5 py-2.5">Type</th>
                <th className="px-5 py-2.5">Symbole</th>
                <th className="px-5 py-2.5 text-right">Quantite</th>
                <th className="px-5 py-2.5 text-right">Prix</th>
                <th className="px-5 py-2.5 text-right">Total</th>
              </tr>
            </thead>
            <tbody>
              {[...state.transactions].reverse().map((tx) => (
                <tr
                  key={tx.id}
                  className="border-b border-slate-50 last:border-none"
                >
                  <td className="px-5 py-2.5 text-xs text-slate-500">
                    {tx.date}
                  </td>
                  <td className="px-5 py-2.5">
                    <span
                      className={`rounded-md px-2 py-0.5 text-xs font-bold ${
                        tx.type === "BUY"
                          ? "bg-success/10 text-success"
                          : "bg-danger/10 text-danger"
                      }`}
                    >
                      {tx.type === "BUY" ? "ACHAT" : "VENTE"}
                    </span>
                  </td>
                  <td className="px-5 py-2.5 text-sm font-semibold text-slate-800">
                    {tx.symbol}
                  </td>
                  <td className="px-5 py-2.5 text-right text-sm text-slate-600">
                    {tx.shares}
                  </td>
                  <td className="px-5 py-2.5 text-right text-sm text-slate-600">
                    ${tx.price.toFixed(2)}
                  </td>
                  <td className="px-5 py-2.5 text-right text-sm font-semibold text-slate-800">
                    ${(tx.price * tx.shares).toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
