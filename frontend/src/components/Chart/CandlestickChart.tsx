import { useEffect, useRef, useState, useCallback } from "react";
import {
  createChart,
  IChartApi,
  ISeriesApi,
  CandlestickData,
  HistogramData,
  LineData,
  CrosshairMode,
} from "lightweight-charts";
import { useStockHistory, useIndicators } from "../../hooks/useStock";

interface Props {
  ticker: string;
  advanced: boolean;
}

const PERIODS = [
  { label: "1J", value: "1d" },
  { label: "1S", value: "1w" },
  { label: "1M", value: "1m" },
  { label: "3M", value: "3m" },
  { label: "1A", value: "1y" },
];

export default function CandlestickChart({ ticker, advanced }: Props) {
  const [period, setPeriod] = useState("1m");
  const { candles, loading, error } = useStockHistory(ticker, period);
  const { data: indicators } = useIndicators(
    advanced ? ticker : undefined,
    "ma20,ma50,bb",
    period
  );

  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const mainSeriesRef = useRef<ISeriesApi<"Candlestick"> | ISeriesApi<"Line"> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<"Histogram"> | null>(null);
  const overlaySeriesRef = useRef<ISeriesApi<"Line">[]>([]);

  const [tooltip, setTooltip] = useState<{
    visible: boolean;
    x: number;
    y: number;
    data: { o: number; h: number; l: number; c: number; v: number } | null;
  }>({ visible: false, x: 0, y: 0, data: null });

  const buildChart = useCallback(() => {
    if (!containerRef.current) return;

    if (chartRef.current) {
      chartRef.current.remove();
      chartRef.current = null;
      mainSeriesRef.current = null;
      volumeSeriesRef.current = null;
      overlaySeriesRef.current = [];
    }

    const chart = createChart(containerRef.current, {
      width: containerRef.current.clientWidth,
      height: 420,
      layout: { background: { color: "#ffffff" }, textColor: "#64748b" },
      grid: {
        vertLines: { color: "#f1f5f9" },
        horzLines: { color: "#f1f5f9" },
      },
      crosshair: { mode: CrosshairMode.Normal },
      rightPriceScale: { borderColor: "#e2e8f0" },
      timeScale: { borderColor: "#e2e8f0", timeVisible: period === "1d" },
    });

    chartRef.current = chart;

    // Volume histogram
    const volumeSeries = chart.addHistogramSeries({
      priceFormat: { type: "volume" },
      priceScaleId: "volume",
    });
    chart.priceScale("volume").applyOptions({
      scaleMargins: { top: 0.8, bottom: 0 },
    });
    volumeSeriesRef.current = volumeSeries;

    if (advanced) {
      const candleSeries = chart.addCandlestickSeries({
        upColor: "#16a34a",
        downColor: "#dc2626",
        borderUpColor: "#16a34a",
        borderDownColor: "#dc2626",
        wickUpColor: "#16a34a",
        wickDownColor: "#dc2626",
      });
      mainSeriesRef.current = candleSeries;
    } else {
      const lineSeries = chart.addLineSeries({
        color: "#3b82f6",
        lineWidth: 2,
      });
      mainSeriesRef.current = lineSeries;
    }

    // Crosshair tooltip
    chart.subscribeCrosshairMove((param) => {
      if (!param.time || !param.point) {
        setTooltip((t) => ({ ...t, visible: false }));
        return;
      }
      const mainData = param.seriesData.get(mainSeriesRef.current!);
      if (mainData) {
        const d = mainData as CandlestickData;
        setTooltip({
          visible: true,
          x: param.point.x,
          y: param.point.y,
          data: {
            o: d.open ?? (d as unknown as LineData).value ?? 0,
            h: d.high ?? (d as unknown as LineData).value ?? 0,
            l: d.low ?? (d as unknown as LineData).value ?? 0,
            c: d.close ?? (d as unknown as LineData).value ?? 0,
            v: 0,
          },
        });
      }
    });

    function handleResize() {
      if (containerRef.current && chartRef.current) {
        chartRef.current.applyOptions({ width: containerRef.current.clientWidth });
      }
    }
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, [advanced, period]);

  useEffect(() => {
    const cleanup = buildChart();
    return () => {
      cleanup?.();
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }
    };
  }, [buildChart]);

  useEffect(() => {
    if (!chartRef.current || !mainSeriesRef.current || candles.length === 0) return;

    if (advanced) {
      const candleData: CandlestickData[] = candles.map((c) => ({
        time: c.time,
        open: c.open,
        high: c.high,
        low: c.low,
        close: c.close,
      }));
      (mainSeriesRef.current as ISeriesApi<"Candlestick">).setData(candleData);
    } else {
      const lineData: LineData[] = candles.map((c) => ({
        time: c.time,
        value: c.close,
      }));
      (mainSeriesRef.current as ISeriesApi<"Line">).setData(lineData);
    }

    // Volume
    if (volumeSeriesRef.current) {
      const volData: HistogramData[] = candles.map((c, i) => ({
        time: c.time,
        value: c.volume,
        color: i > 0 && c.close >= candles[i - 1].close ? "#16a34a40" : "#dc262640",
      }));
      volumeSeriesRef.current.setData(volData);
    }

    chartRef.current.timeScale().fitContent();
  }, [candles, advanced]);

  // Overlays (MA, Bollinger)
  useEffect(() => {
    if (!chartRef.current || !advanced || !indicators || candles.length === 0) return;

    // Remove old overlays
    for (const s of overlaySeriesRef.current) {
      chartRef.current.removeSeries(s);
    }
    overlaySeriesRef.current = [];

    const times = candles.map((c) => c.time);

    const addOverlay = (values: (number | null)[] | undefined, color: string) => {
      if (!values || !chartRef.current) return;
      const series = chartRef.current.addLineSeries({ color, lineWidth: 1 });
      const data: LineData[] = [];
      for (let i = 0; i < Math.min(values.length, times.length); i++) {
        if (values[i] != null) {
          data.push({ time: times[i], value: values[i]! });
        }
      }
      series.setData(data);
      overlaySeriesRef.current.push(series);
    };

    addOverlay(indicators.ma20, "#f59e0b");
    addOverlay(indicators.ma50, "#8b5cf6");

    if (indicators.bollinger) {
      addOverlay(indicators.bollinger.upper, "#94a3b880");
      addOverlay(indicators.bollinger.lower, "#94a3b880");
    }
  }, [indicators, candles, advanced]);

  return (
    <div>
      <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        {PERIODS.map((p) => (
          <button
            key={p.value}
            onClick={() => setPeriod(p.value)}
            style={{
              padding: "6px 14px",
              borderRadius: 6,
              border: "1px solid #e2e8f0",
              background: period === p.value ? "#0ea5e9" : "#fff",
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

      {advanced && (
        <div style={{ display: "flex", gap: 16, marginBottom: 8, fontSize: 12 }}>
          <span>
            <span style={{ color: "#f59e0b", fontWeight: 700 }}>---</span> MA20
          </span>
          <span>
            <span style={{ color: "#8b5cf6", fontWeight: 700 }}>---</span> MA50
          </span>
          <span>
            <span style={{ color: "#94a3b8", fontWeight: 700 }}>---</span> Bollinger
          </span>
        </div>
      )}

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
          position: "relative",
        }}
      >
        {tooltip.visible && tooltip.data && advanced && (
          <div
            style={{
              position: "absolute",
              left: 12,
              top: 12,
              background: "rgba(255,255,255,0.95)",
              border: "1px solid #e2e8f0",
              borderRadius: 6,
              padding: "8px 12px",
              fontSize: 12,
              zIndex: 10,
              pointerEvents: "none",
              display: "flex",
              gap: 12,
            }}
          >
            <span>O: <b>${tooltip.data.o.toFixed(2)}</b></span>
            <span>H: <b>${tooltip.data.h.toFixed(2)}</b></span>
            <span>L: <b>${tooltip.data.l.toFixed(2)}</b></span>
            <span>C: <b>${tooltip.data.c.toFixed(2)}</b></span>
          </div>
        )}
      </div>
    </div>
  );
}
