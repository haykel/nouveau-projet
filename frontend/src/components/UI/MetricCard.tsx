interface Props {
  icon: string;
  title: string;
  value: string;
  changePercent?: number | null;
  subtitle?: string;
}

export default function MetricCard({ icon, title, value, changePercent, subtitle }: Props) {
  const isPositive = (changePercent ?? 0) >= 0;

  return (
    <div className="rounded-xl bg-white p-5 shadow-sm">
      <div className="mb-3 flex items-center justify-between">
        <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-lg">
          {icon}
        </span>
        {changePercent != null && (
          <span
            className={`rounded-md px-2.5 py-1 text-xs font-bold ${
              isPositive
                ? "bg-success/10 text-success"
                : "bg-danger/10 text-danger"
            }`}
          >
            {isPositive ? "+" : ""}
            {changePercent.toFixed(2)}%
          </span>
        )}
      </div>
      <div className="mb-0.5 text-xs font-medium text-slate-400">{title}</div>
      <div className="text-xl font-bold text-slate-800">{value}</div>
      {subtitle && (
        <div className="mt-1 text-xs text-slate-400">{subtitle}</div>
      )}
    </div>
  );
}
