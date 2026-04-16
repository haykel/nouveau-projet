import { useCallback, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useStockDetail, useScore, useIndicators } from "../hooks/useStock";
import CandlestickChart from "../components/Chart/CandlestickChart";
import IndicatorPanel from "../components/Chart/IndicatorPanel";
import StockScore from "../components/StockScore/StockScore";
import ModeToggle from "../components/Chart/ModeToggle";
import SourceBadge from "../components/UI/SourceBadge";

export default function Stock() {
  const { ticker } = useParams<{ ticker: string }>();
  const navigate = useNavigate();
  const { quote, loading, error, refresh } = useStockDetail(ticker);
  const { score } = useScore(ticker);
  const [advanced, setAdvanced] = useState(
    () => localStorage.getItem("chart-mode-advanced") === "true"
  );
  const { data: indicators } = useIndicators(
    advanced ? ticker : undefined,
    "rsi,macd,ma20,ma50,bb",
    "3m"
  );

  const handleModeChange = useCallback((adv: boolean) => {
    setAdvanced(adv);
  }, []);

  const isPositive = (quote?.change ?? 0) >= 0;

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate("/")}
          className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-50"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
          Retour
        </button>
        <ModeToggle onChange={handleModeChange} />
      </div>

      {loading && !quote && (
        <div className="py-12 text-center text-slate-400">Chargement...</div>
      )}

      {error && (
        <div className="py-12 text-center text-danger">{error}</div>
      )}

      {quote && (
        <>
          {/* Stock header card */}
          <div className="rounded-xl bg-white p-6 shadow-sm">
            <div className="mb-4 flex flex-wrap items-start justify-between gap-4">
              <div>
                <div className="mb-1 flex items-center gap-3">
                  <h1 className="text-2xl font-bold text-slate-800">
                    {quote.symbol}
                  </h1>
                  <SourceBadge source="finnhub" />
                </div>
                <div className="flex items-baseline gap-3">
                  <span className="text-3xl font-bold text-slate-800">
                    ${quote.current_price.toFixed(2)}
                  </span>
                  <span
                    className={`text-lg font-bold ${
                      isPositive ? "text-success" : "text-danger"
                    }`}
                  >
                    {isPositive ? "+" : ""}
                    {quote.change?.toFixed(2)} ({isPositive ? "+" : ""}
                    {quote.change_percent?.toFixed(2)}%)
                  </span>
                </div>
              </div>
              <button
                onClick={refresh}
                className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-50"
              >
                Actualiser
              </button>
            </div>
          </div>

          {/* Score */}
          {score && <StockScore score={score} />}

          {/* Stats grid */}
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            {[
              { label: "Volume", value: quote.volume?.toLocaleString() },
              { label: "Plus haut", value: quote.high != null ? `$${quote.high.toFixed(2)}` : null },
              { label: "Plus bas", value: quote.low != null ? `$${quote.low.toFixed(2)}` : null },
              { label: "Ouverture", value: quote.open != null ? `$${quote.open.toFixed(2)}` : null },
              {
                label: "Cloture prec.",
                value: quote.previous_close != null ? `$${quote.previous_close.toFixed(2)}` : null,
              },
            ]
              .filter((item) => item.value != null)
              .map((item) => (
                <div
                  key={item.label}
                  className="rounded-xl bg-white p-4 shadow-sm"
                >
                  <div className="mb-1 text-xs font-medium text-slate-400">
                    {item.label}
                  </div>
                  <div className="text-lg font-bold text-slate-800">
                    {item.value}
                  </div>
                </div>
              ))}
          </div>

          {/* Chart */}
          <div className="rounded-xl bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-base font-semibold text-slate-800">
              {advanced ? "Graphique en chandeliers" : "Historique des prix"}
            </h2>
            <CandlestickChart ticker={ticker!} advanced={advanced} />
          </div>

          {/* Indicator panels */}
          {advanced && indicators && (
            <div className="rounded-xl bg-white p-6 shadow-sm">
              <h2 className="mb-4 text-base font-semibold text-slate-800">
                Indicateurs techniques
              </h2>
              <IndicatorPanel
                indicators={indicators}
                timestamps={indicators.timestamps}
              />
            </div>
          )}

          <div className="text-center text-xs text-slate-400">
            Mise a jour automatique toutes les 60s
          </div>
        </>
      )}
    </div>
  );
}
