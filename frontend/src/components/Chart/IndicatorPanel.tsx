import { useEffect, useRef, useState } from "react";
import { createChart, IChartApi, UTCTimestamp, LineData, HistogramData } from "lightweight-charts";
import type { IndicatorsData } from "../../services/api";

interface Props {
  indicators: IndicatorsData;
  timestamps: number[];
}

export default function IndicatorPanel({ indicators, timestamps }: Props) {
  const [showRSI, setShowRSI] = useState(true);
  const [showMACD, setShowMACD] = useState(true);

  return (
    <div>
      <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
        <ToggleButton label="RSI" active={showRSI} onClick={() => setShowRSI(!showRSI)} />
        <ToggleButton label="MACD" active={showMACD} onClick={() => setShowMACD(!showMACD)} />
      </div>

      {showRSI && indicators.rsi && (
        <RSIPanel rsi={indicators.rsi} timestamps={timestamps} />
      )}

      {showMACD && indicators.macd && (
        <MACDPanel macd={indicators.macd} timestamps={timestamps} />
      )}
    </div>
  );
}

function ToggleButton({
  label,
  active,
  onClick,
}: {
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      style={{
        padding: "4px 12px",
        borderRadius: 6,
        border: "1px solid #e2e8f0",
        background: active ? "#0ea5e9" : "#fff",
        color: active ? "#fff" : "#64748b",
        fontWeight: 600,
        fontSize: 12,
        cursor: "pointer",
      }}
    >
      {label}
    </button>
  );
}

function RSIPanel({ rsi, timestamps }: { rsi: (number | null)[]; timestamps: number[] }) {
  const ref = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);

  useEffect(() => {
    if (!ref.current) return;

    const chart = createChart(ref.current, {
      width: ref.current.clientWidth,
      height: 120,
      layout: { background: { color: "#ffffff" }, textColor: "#64748b" },
      grid: { vertLines: { color: "#f8fafc" }, horzLines: { color: "#f1f5f9" } },
      rightPriceScale: { borderColor: "#e2e8f0" },
      timeScale: { visible: false },
    });
    chartRef.current = chart;

    const series = chart.addLineSeries({ color: "#8b5cf6", lineWidth: 2 });
    const data: LineData[] = [];
    for (let i = 0; i < Math.min(rsi.length, timestamps.length); i++) {
      if (rsi[i] != null) {
        data.push({ time: timestamps[i] as UTCTimestamp, value: rsi[i]! });
      }
    }
    series.setData(data);

    // Overbought/oversold lines
    const overBought = chart.addLineSeries({ color: "#dc262640", lineWidth: 1, lineStyle: 2 });
    const overSold = chart.addLineSeries({ color: "#16a34a40", lineWidth: 1, lineStyle: 2 });

    const tData70: LineData[] = data.map((d) => ({ time: d.time, value: 70 }));
    const tData30: LineData[] = data.map((d) => ({ time: d.time, value: 30 }));
    overBought.setData(tData70);
    overSold.setData(tData30);

    chart.timeScale().fitContent();

    function handleResize() {
      if (ref.current && chartRef.current) {
        chartRef.current.applyOptions({ width: ref.current.clientWidth });
      }
    }
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
      chartRef.current = null;
    };
  }, [rsi, timestamps]);

  return (
    <div style={{ marginBottom: 16 }}>
      <div style={{ fontSize: 12, fontWeight: 600, color: "#64748b", marginBottom: 4 }}>
        RSI (14)
        <span style={{ fontSize: 11, fontWeight: 400, marginLeft: 8 }}>
          <span style={{ color: "#dc2626" }}>70</span> Surachat
          {" / "}
          <span style={{ color: "#16a34a" }}>30</span> Survente
        </span>
      </div>
      <div
        ref={ref}
        style={{ width: "100%", borderRadius: 8, overflow: "hidden", border: "1px solid #f1f5f9" }}
      />
    </div>
  );
}

function MACDPanel({
  macd,
  timestamps,
}: {
  macd: { macd: (number | null)[]; signal: (number | null)[]; histogram: (number | null)[] };
  timestamps: number[];
}) {
  const ref = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);

  useEffect(() => {
    if (!ref.current) return;

    const chart = createChart(ref.current, {
      width: ref.current.clientWidth,
      height: 120,
      layout: { background: { color: "#ffffff" }, textColor: "#64748b" },
      grid: { vertLines: { color: "#f8fafc" }, horzLines: { color: "#f1f5f9" } },
      rightPriceScale: { borderColor: "#e2e8f0" },
      timeScale: { visible: false },
    });
    chartRef.current = chart;

    // Histogram
    const histSeries = chart.addHistogramSeries({});
    const histData: HistogramData[] = [];
    for (let i = 0; i < Math.min(macd.histogram.length, timestamps.length); i++) {
      if (macd.histogram[i] != null) {
        histData.push({
          time: timestamps[i] as UTCTimestamp,
          value: macd.histogram[i]!,
          color: macd.histogram[i]! >= 0 ? "#16a34a80" : "#dc262680",
        });
      }
    }
    histSeries.setData(histData);

    // MACD line
    const macdSeries = chart.addLineSeries({ color: "#0ea5e9", lineWidth: 2 });
    const macdData: LineData[] = [];
    for (let i = 0; i < Math.min(macd.macd.length, timestamps.length); i++) {
      if (macd.macd[i] != null) {
        macdData.push({ time: timestamps[i] as UTCTimestamp, value: macd.macd[i]! });
      }
    }
    macdSeries.setData(macdData);

    // Signal line
    const signalSeries = chart.addLineSeries({ color: "#f59e0b", lineWidth: 2 });
    const signalData: LineData[] = [];
    for (let i = 0; i < Math.min(macd.signal.length, timestamps.length); i++) {
      if (macd.signal[i] != null) {
        signalData.push({ time: timestamps[i] as UTCTimestamp, value: macd.signal[i]! });
      }
    }
    signalSeries.setData(signalData);

    chart.timeScale().fitContent();

    function handleResize() {
      if (ref.current && chartRef.current) {
        chartRef.current.applyOptions({ width: ref.current.clientWidth });
      }
    }
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
      chartRef.current = null;
    };
  }, [macd, timestamps]);

  return (
    <div style={{ marginBottom: 16 }}>
      <div style={{ fontSize: 12, fontWeight: 600, color: "#64748b", marginBottom: 4 }}>
        MACD (12, 26, 9)
        <span style={{ fontSize: 11, fontWeight: 400, marginLeft: 8 }}>
          <span style={{ color: "#0ea5e9" }}>MACD</span>
          {" / "}
          <span style={{ color: "#f59e0b" }}>Signal</span>
        </span>
      </div>
      <div
        ref={ref}
        style={{ width: "100%", borderRadius: 8, overflow: "hidden", border: "1px solid #f1f5f9" }}
      />
    </div>
  );
}
