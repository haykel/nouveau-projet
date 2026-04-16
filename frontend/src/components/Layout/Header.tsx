import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useKeycloak } from "../KeycloakProvider";
import { useStockSearch } from "../../hooks/useStock";

interface Props {
  onMenuClick: () => void;
}

export default function Header({ onMenuClick }: Props) {
  const { username } = useKeycloak();
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const { results, loading } = useStockSearch(query);
  const ref = useRef<HTMLDivElement>(null);
  const [now, setNow] = useState(new Date());

  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  function handleSelect(symbol: string) {
    setQuery("");
    setOpen(false);
    navigate(`/stock/${symbol}`);
  }

  const dateStr = now.toLocaleDateString("fr-FR", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });
  const timeStr = now.toLocaleTimeString("fr-FR", {
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b border-slate-200 bg-white px-4 shadow-sm lg:px-6">
      {/* Mobile menu button */}
      <button
        onClick={onMenuClick}
        className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 lg:hidden"
      >
        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      {/* Search */}
      <div ref={ref} className="relative max-w-md flex-1">
        <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
          <svg className="h-4 w-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <input
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setOpen(true);
          }}
          onFocus={() => setOpen(true)}
          placeholder="Rechercher une action (ex: AAPL, MSFT...)"
          className="w-full rounded-lg border border-slate-200 bg-slate-50 py-2 pr-4 pl-10 text-sm text-slate-700 placeholder-slate-400 outline-none transition-colors focus:border-primary focus:bg-white focus:ring-1 focus:ring-primary"
        />

        {open && query.length > 0 && (
          <div className="absolute top-full right-0 left-0 z-50 mt-1 max-h-72 overflow-y-auto rounded-lg border border-slate-200 bg-white shadow-lg">
            {loading && (
              <div className="px-4 py-3 text-sm text-slate-400">
                Recherche...
              </div>
            )}
            {!loading && results.length === 0 && (
              <div className="px-4 py-3 text-sm text-slate-400">
                Aucun resultat
              </div>
            )}
            {results.map((item) => (
              <button
                key={item.symbol}
                onClick={() => handleSelect(item.symbol)}
                className="flex w-full items-center justify-between px-4 py-2.5 text-left transition-colors hover:bg-slate-50"
              >
                <div>
                  <div className="text-sm font-semibold text-slate-800">
                    {item.symbol}
                  </div>
                  <div className="text-xs text-slate-500">
                    {item.description}
                  </div>
                </div>
                <span className="text-xs text-slate-400">{item.type}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Right side */}
      <div className="flex items-center gap-4">
        {/* Date/time */}
        <div className="hidden text-right md:block">
          <div className="text-xs font-medium capitalize text-slate-700">
            {dateStr}
          </div>
          <div className="text-xs text-slate-400">{timeStr}</div>
        </div>

        {/* Notifications */}
        <button className="relative rounded-lg p-2 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600">
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
          <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-danger" />
        </button>

        {/* User avatar */}
        <div className="hidden items-center gap-2 lg:flex">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-xs font-bold text-white">
            {username?.charAt(0).toUpperCase() || "U"}
          </div>
          <span className="text-sm font-medium text-slate-700">
            {username}
          </span>
        </div>
      </div>
    </header>
  );
}
