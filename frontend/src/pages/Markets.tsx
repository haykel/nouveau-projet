import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getIndices, getTop10, MarketIndex, StockQuote } from "../services/api";

const SECTORS = [
  { name: "Tech", tickers: ["AAPL", "MSFT", "GOOGL", "NVDA", "META", "ADBE"] },
  { name: "Finance", tickers: ["JPM", "BAC", "GS", "MS", "V", "MA"] },
  { name: "E-commerce", tickers: ["AMZN", "SHOP", "PYPL", "SQ"] },
  { name: "Auto & Energie", tickers: ["TSLA", "UBER", "LYFT"] },
];

export default function Markets() {
  const navigate = useNavigate();
  const [indices, setIndices] = useState<MarketIndex[]>([]);
  const [top10, setTop10] = useState<StockQuote[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getIndices().catch(() => []),
      getTop10().catch(() => []),
    ]).then(([idx, t10]) => {
      setIndices(idx);
      setTop10(t10);
      setLoading(false);
    });
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-slate-800">Marches</h1>

      {/* Indices */}
      <section>
        <h2 className="mb-4 text-base font-semibold text-slate-800">
          Indices mondiaux
        </h2>
        {loading ? (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-24 animate-pulse rounded-xl bg-white" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {indices.map((idx) => (
              <div
                key={idx.symbol}
                className="rounded-xl bg-white p-5 shadow-sm"
              >
                <div className="mb-2 text-sm font-medium text-slate-500">
                  {idx.name}
                </div>
                {idx.current_price != null ? (
                  <>
                    <div className="text-xl font-bold text-slate-800">
                      ${idx.current_price.toFixed(2)}
                    </div>
                    <div
                      className={`mt-1 text-sm font-semibold ${
                        (idx.change_percent ?? 0) >= 0
                          ? "text-success"
                          : "text-danger"
                      }`}
                    >
                      {(idx.change_percent ?? 0) >= 0 ? "+" : ""}
                      {idx.change_percent?.toFixed(2)}%
                      <span className="ml-2 text-xs text-slate-400">
                        ({(idx.change ?? 0) >= 0 ? "+" : ""}
                        {idx.change?.toFixed(2)})
                      </span>
                    </div>
                  </>
                ) : (
                  <div className="text-sm text-slate-400">Indisponible</div>
                )}
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Heatmap */}
      <section>
        <h2 className="mb-4 text-base font-semibold text-slate-800">
          Heatmap des variations
        </h2>
        {top10.length === 0 ? (
          <div className="text-sm text-slate-400">Chargement...</div>
        ) : (
          <div className="grid grid-cols-3 gap-2 sm:grid-cols-5 lg:grid-cols-10">
            {top10.map((stock) => {
              const pct = stock.change_percent ?? 0;
              const intensity = Math.min(Math.abs(pct) * 20, 100);
              const bg =
                pct >= 0
                  ? `rgba(34,197,94,${intensity / 100})`
                  : `rgba(239,68,68,${intensity / 100})`;

              return (
                <div
                  key={stock.symbol}
                  onClick={() => navigate(`/stock/${stock.symbol}`)}
                  className="cursor-pointer rounded-lg p-3 text-center transition-transform hover:scale-105"
                  style={{ backgroundColor: bg }}
                >
                  <div className="text-xs font-bold text-slate-800">
                    {stock.symbol}
                  </div>
                  <div
                    className={`text-xs font-semibold ${
                      pct >= 0 ? "text-green-800" : "text-red-800"
                    }`}
                  >
                    {pct >= 0 ? "+" : ""}
                    {pct.toFixed(1)}%
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>

      {/* Sectors */}
      <section>
        <h2 className="mb-4 text-base font-semibold text-slate-800">
          Actions par secteur
        </h2>
        <div className="space-y-6">
          {SECTORS.map((sector) => (
            <div key={sector.name}>
              <h3 className="mb-3 text-sm font-semibold text-slate-600">
                {sector.name}
              </h3>
              <div className="overflow-hidden rounded-xl bg-white shadow-sm">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-slate-100 text-left text-xs font-medium text-slate-400">
                      <th className="px-5 py-2.5">Symbole</th>
                      <th className="px-5 py-2.5 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sector.tickers.map((t) => (
                      <tr
                        key={t}
                        onClick={() => navigate(`/stock/${t}`)}
                        className="cursor-pointer border-b border-slate-50 transition-colors last:border-none hover:bg-slate-50"
                      >
                        <td className="px-5 py-2.5 text-sm font-semibold text-slate-800">
                          {t}
                        </td>
                        <td className="px-5 py-2.5 text-right">
                          <span className="text-xs font-medium text-primary">
                            Voir &rarr;
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
