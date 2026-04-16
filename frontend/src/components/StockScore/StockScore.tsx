import type { ScoreData } from "../../services/api";

interface Props {
  score: ScoreData;
}

export default function StockScore({ score }: Props) {
  const getColor = (value: number) => {
    if (value >= 65) return "#16a34a";
    if (value >= 40) return "#f59e0b";
    return "#dc2626";
  };

  const getSignalEmoji = (signal: string) => {
    if (signal === "ACHAT") return "\uD83D\uDFE2";
    if (signal === "NEUTRE") return "\uD83D\uDFE1";
    return "\uD83D\uDD34";
  };

  const getSignalLabel = (signal: string) => {
    if (signal === "ACHAT") return "Signal d'achat";
    if (signal === "NEUTRE") return "Neutre";
    return "Signal de vente";
  };

  const color = getColor(score.score);
  const pct = score.score / 100;

  return (
    <div
      style={{
        background: "#fff",
        border: "1px solid #e2e8f0",
        borderRadius: 12,
        padding: 24,
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: 16,
        }}
      >
        <h3 style={{ fontSize: 16, fontWeight: 600, margin: 0 }}>
          Score de sante
        </h3>
        <div
          style={{
            fontSize: 14,
            fontWeight: 700,
            color,
            display: "flex",
            alignItems: "center",
            gap: 6,
          }}
        >
          {getSignalEmoji(score.signal)} {getSignalLabel(score.signal)}
        </div>
      </div>

      {/* Gauge */}
      <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 16 }}>
        <div
          style={{
            fontSize: 36,
            fontWeight: 800,
            color,
            minWidth: 70,
            textAlign: "center",
          }}
        >
          {score.score}
        </div>
        <div style={{ flex: 1 }}>
          <div
            style={{
              height: 10,
              borderRadius: 5,
              background: "#f1f5f9",
              overflow: "hidden",
            }}
          >
            <div
              style={{
                height: "100%",
                width: `${pct * 100}%`,
                borderRadius: 5,
                background: `linear-gradient(90deg, #dc2626 0%, #f59e0b 50%, #16a34a 100%)`,
                backgroundSize: "200% 100%",
                backgroundPosition: `${(1 - pct) * 100}% 0`,
                transition: "width 0.5s",
              }}
            />
          </div>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              fontSize: 11,
              color: "#94a3b8",
              marginTop: 4,
            }}
          >
            <span>Vente</span>
            <span>Neutre</span>
            <span>Achat</span>
          </div>
        </div>
      </div>

      {/* Detail scores */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: 8,
          marginBottom: 16,
        }}
      >
        {[
          { label: "RSI", value: score.details.rsi_score, sub: `RSI: ${score.details.rsi}` },
          { label: "Tendance", value: score.details.trend_score },
          { label: "Volume", value: score.details.volume_score },
          { label: "Volatilite", value: score.details.volatility_score },
        ].map((item) => (
          <div
            key={item.label}
            style={{
              background: "#f8fafc",
              borderRadius: 8,
              padding: "10px 12px",
              textAlign: "center",
            }}
          >
            <div style={{ fontSize: 11, color: "#94a3b8", marginBottom: 2 }}>
              {item.label}
            </div>
            <div
              style={{
                fontSize: 18,
                fontWeight: 700,
                color: getColor(item.value),
              }}
            >
              {item.value}
            </div>
            {item.sub && (
              <div style={{ fontSize: 11, color: "#94a3b8" }}>{item.sub}</div>
            )}
          </div>
        ))}
      </div>

      {/* Explanation */}
      <p style={{ fontSize: 14, color: "#475569", lineHeight: 1.5, margin: "0 0 12px" }}>
        {score.explanation}
      </p>

      <p
        style={{
          fontSize: 11,
          color: "#94a3b8",
          fontStyle: "italic",
          margin: 0,
        }}
      >
        A titre informatif uniquement. Ne constitue pas un conseil en investissement.
      </p>
    </div>
  );
}
