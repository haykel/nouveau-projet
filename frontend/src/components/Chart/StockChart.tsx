import { useEffect, useRef, useState } from "react";
import { createChart, IChartApi, ISeriesApi, LineData } from "lightweight-charts";
import { useStockHistory } from "../../hooks/useStock";

interface Props {
  ticker: string;
}

const PERIODS = [
  { label: "1J", value: "1d" },
  { label: "1S", value: "1w" },
  { label: "1M", value: "1m" },
  { label: "3M", value: "3m" },
  { label: "1A", value: "1y" },
];

export default function StockChart({ ticker }: Props) {
  const [period, setPeriod] = useState("1m");
  const { candles, loading, error } = useStockHistory(ticker, period);
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<"Line"> | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const chart = createChart(containerRef.current, {
      width: containerRef.current.clientWidth,
      height: 350,
      layout: {
        background: { color: "#ffffff" },
        textColor: "#64748b",
      },
      grid: {
        vertLines: { color: "#f1f5f9" },
        horzLines: { color: "#f1f5f9" },
      },
      rightPriceScale: { borderColor: "#e2e8f0" },
      timeScale: { borderColor: "#e2e8f0" },
    });

    const series = chart.addLineSeries({
      color: "#3b82f6",
      lineWidth: 2,
    });

    chartRef.current = chart;
    seriesRef.current = series;

    function handleResize() {
      if (containerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: containerRef.current.clientWidth,
        });
      }
    }
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
      chartRef.current = null;
      seriesRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!seriesRef.current || candles.length === 0) return;

    const lineData: LineData[] = candles.map((c) => ({
      time: c.time,
      value: c.close,
    }));

    seriesRef.current.setData(lineData);
    chartRef.current?.timeScale().fitContent();
  }, [candles]);

  return (
    <div>
      <div
        style={{
          display: "flex",
          gap: 8,
          marginBottom: 16,
        }}
      >
        {PERIODS.map((p) => (
          <button
            key={p.value}
            onClick={() => setPeriod(p.value)}
            style={{
              padding: "6px 14px",
              borderRadius: 6,
              border: "1px solid #e2e8f0",
              background: period === p.value ? "#3b82f6" : "#fff",
              color: period === p.value ? "#fff" : "#64748b",
              fontWeight: 600,
              fontSize: 13,
              cursor: "pointer",
            }}
          >
            {p.label}
          </button>
        ))}
      </div>

      {loading && (
        <div style={{ padding: 40, textAlign: "center", color: "#94a3b8" }}>
          Chargement du graphique...
        </div>
      )}

      {error && (
        <div style={{ padding: 40, textAlign: "center", color: "#dc2626" }}>
          {error}
        </div>
      )}

      <div
        ref={containerRef}
        style={{
          width: "100%",
          borderRadius: 8,
          overflow: "hidden",
          display: loading ? "none" : "block",
        }}
      />
    </div>
  );
}
