type Source = "finnhub" | "yahoo" | "alphavantage";

interface Props {
  source: Source;
}

const CONFIG: Record<Source, { dot: string; label: string; bg: string; text: string }> = {
  finnhub: {
    dot: "bg-success",
    label: "Finnhub (temps reel)",
    bg: "bg-success/10",
    text: "text-success",
  },
  yahoo: {
    dot: "bg-blue-500",
    label: "Yahoo Finance",
    bg: "bg-blue-50",
    text: "text-blue-600",
  },
  alphavantage: {
    dot: "bg-amber-500",
    label: "Alpha Vantage",
    bg: "bg-amber-50",
    text: "text-amber-600",
  },
};

export default function SourceBadge({ source }: Props) {
  const cfg = CONFIG[source];

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ${cfg.bg} ${cfg.text}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${cfg.dot}`} />
      {cfg.label}
    </span>
  );
}
