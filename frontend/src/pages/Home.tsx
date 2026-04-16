import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import MetricCard from "../components/UI/MetricCard";
import { getIndices, getStock, getTop10, MarketIndex, StockQuote } from "../services/api";

const POPULAR_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA"];

export default function Home() {
  const navigate = useNavigate();
  const [indices, setIndices] = useState<MarketIndex[]>([]);
  const [popular, setPopular] = useState<StockQuote[]>([]);
  const [top10, setTop10] = useState<StockQuote[]>([]);
  const [loadingIndices, setLoadingIndices] = useState(true);
  const [loadingPopular, setLoadingPopular] = useState(true);
  const [loadingTop10, setLoadingTop10] = useState(true);

  useEffect(() => {
    getIndices()
      .then(setIndices)
      .catch(() => {})
      .finally(() => setLoadingIndices(false));

    Promise.all(POPULAR_TICKERS.map((t) => getStock(t).catch(() => null)))
      .then((results) => setPopular(results.filter(Boolean) as StockQuote[]))
      .finally(() => setLoadingPopular(false));

    getTop10()
      .then(setTop10)
      .catch(() => {})
      .finally(() => setLoadingTop10(false));
  }, []);

  return (
    <div className="space-y-6">
      {/* Metric cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {loadingIndices ? (
          Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-[120px] animate-pulse rounded-xl bg-white" />
          ))
        ) : (
          indices.slice(0, 4).map((idx) => (
            <MetricCard
              key={idx.symbol}
              icon={idx.name === "S&P 500" ? "\u{1F4C8}" : idx.name === "NASDAQ" ? "\u{1F4BB}" : idx.name === "Dow Jones" ? "\u{1F3ED}" : "\u{1F1EB}\u{1F1F7}"}
              title={idx.name}
              value={idx.current_price != null ? `$${idx.current_price.toFixed(2)}` : "N/A"}
              changePercent={idx.change_percent}
              subtitle={idx.symbol}
            />
          ))
        )}
      </div>

      {/* Indices boursiers */}
      <section>
        <h2 className="mb-4 text-lg font-semibold text-slate-800">
          Indices boursiers
        </h2>
        {loadingIndices ? (
          <div className="text-sm text-slate-400">Chargement...</div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {indices.map((idx) => (
              <div
                key={idx.symbol}
                className="rounded-xl bg-white p-5 shadow-sm"
              >
                <div className="mb-1 text-sm text-slate-500">{idx.name}</div>
                {idx.current_price != null ? (
                  <>
                    <div className="text-2xl font-bold text-slate-800">
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

      {/* Top 10 du jour */}
      <section>
        <h2 className="mb-4 text-lg font-semibold text-slate-800">
          Top 10 du jour
        </h2>
        {loadingTop10 ? (
          <div className="text-sm text-slate-400">Chargement...</div>
        ) : top10.length === 0 ? (
          <div className="text-sm text-slate-400">Aucune donnee disponible</div>
        ) : (
          <div className="overflow-hidden rounded-xl bg-white shadow-sm">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-100 text-left text-xs font-medium text-slate-400">
                  <th className="px-5 py-3">#</th>
                  <th className="px-5 py-3">Symbole</th>
                  <th className="px-5 py-3 text-right">Prix</th>
                  <th className="px-5 py-3 text-right">Variation</th>
                </tr>
              </thead>
              <tbody>
                {top10.map((stock, i) => (
                  <tr
                    key={stock.symbol}
                    onClick={() => navigate(`/stock/${stock.symbol}`)}
                    className="cursor-pointer border-b border-slate-50 transition-colors last:border-none hover:bg-slate-50"
                  >
                    <td className="px-5 py-3 text-sm font-bold text-slate-400">
                      {i + 1}
                    </td>
                    <td className="px-5 py-3 text-sm font-bold text-slate-800">
                      {stock.symbol}
                    </td>
                    <td className="px-5 py-3 text-right text-sm text-slate-600">
                      ${stock.current_price.toFixed(2)}
                    </td>
                    <td className="px-5 py-3 text-right">
                      <span className="inline-block rounded-md bg-success/10 px-2.5 py-1 text-xs font-bold text-success">
                        +{stock.change_percent?.toFixed(2)}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Actions populaires */}
      <section>
        <h2 className="mb-4 text-lg font-semibold text-slate-800">
          Actions populaires
        </h2>
        {loadingPopular ? (
          <div className="text-sm text-slate-400">Chargement...</div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {popular.map((stock) => {
              const isPositive = (stock.change ?? 0) >= 0;
              return (
                <div
                  key={stock.symbol}
                  onClick={() => navigate(`/stock/${stock.symbol}`)}
                  className="cursor-pointer rounded-xl bg-white p-5 shadow-sm transition-shadow hover:shadow-md"
                >
                  <div className="mb-3 flex items-start justify-between">
                    <span className="text-base font-bold text-slate-800">
                      {stock.symbol}
                    </span>
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
                  </div>
                  <div className="text-2xl font-bold text-slate-800">
                    ${stock.current_price.toFixed(2)}
                  </div>
                  <div
                    className={`mt-1 text-sm ${
                      isPositive ? "text-success" : "text-danger"
                    }`}
                  >
                    {isPositive ? "+" : ""}
                    {stock.change?.toFixed(2)} aujourd'hui
                  </div>
                  {stock.high != null && stock.low != null && (
                    <div className="mt-3 flex gap-4 text-xs text-slate-400">
                      <span>H: ${stock.high.toFixed(2)}</span>
                      <span>B: ${stock.low.toFixed(2)}</span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}
