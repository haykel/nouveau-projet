import type { StockQuote } from "../../services/api";

interface Props {
  quote: StockQuote;
  onClick?: () => void;
}

export default function StockCard({ quote, onClick }: Props) {
  const isPositive = (quote.change ?? 0) >= 0;
  const color = isPositive ? "#16a34a" : "#dc2626";
  const arrow = isPositive ? "\u25B2" : "\u25BC";
  const sign = isPositive ? "+" : "";

  return (
    <div
      onClick={onClick}
      style={{
        background: "#fff",
        border: "1px solid #e2e8f0",
        borderRadius: 12,
        padding: 20,
        cursor: onClick ? "pointer" : "default",
        transition: "box-shadow 0.2s",
        minWidth: 200,
      }}
      onMouseEnter={(e) => {
        if (onClick) e.currentTarget.style.boxShadow = "0 4px 12px rgba(0,0,0,0.08)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.boxShadow = "none";
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          marginBottom: 12,
        }}
      >
        <div>
          <div style={{ fontSize: 18, fontWeight: 700 }}>{quote.symbol}</div>
        </div>
        <div
          style={{
            background: isPositive ? "#f0fdf4" : "#fef2f2",
            color,
            padding: "4px 10px",
            borderRadius: 6,
            fontSize: 13,
            fontWeight: 600,
          }}
        >
          {arrow} {sign}
          {quote.change_percent?.toFixed(2)}%
        </div>
      </div>

      <div style={{ fontSize: 28, fontWeight: 700, marginBottom: 4 }}>
        ${quote.current_price.toFixed(2)}
      </div>

      <div style={{ fontSize: 14, color }}>
        {sign}
        {quote.change?.toFixed(2)} aujourd'hui
      </div>

      {quote.high != null && quote.low != null && (
        <div
          style={{
            display: "flex",
            gap: 16,
            marginTop: 12,
            fontSize: 13,
            color: "#64748b",
          }}
        >
          <span>H: ${quote.high.toFixed(2)}</span>
          <span>B: ${quote.low.toFixed(2)}</span>
          {quote.open != null && <span>O: ${quote.open.toFixed(2)}</span>}
        </div>
      )}
    </div>
  );
}
