import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useStockSearch } from "../../hooks/useStock";

export default function SearchBar() {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const { results, loading } = useStockSearch(query);
  const navigate = useNavigate();
  const ref = useRef<HTMLDivElement>(null);

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

  return (
    <div ref={ref} style={{ position: "relative", maxWidth: 480, width: "100%" }}>
      <input
        type="text"
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          setOpen(true);
        }}
        onFocus={() => setOpen(true)}
        placeholder="Rechercher une action (ex: AAPL, MSFT...)"
        style={{
          width: "100%",
          padding: "12px 16px",
          fontSize: 16,
          border: "2px solid #e2e8f0",
          borderRadius: 8,
          outline: "none",
          boxSizing: "border-box",
        }}
      />

      {open && query.length > 0 && (
        <div
          style={{
            position: "absolute",
            top: "100%",
            left: 0,
            right: 0,
            background: "#fff",
            border: "1px solid #e2e8f0",
            borderRadius: 8,
            marginTop: 4,
            maxHeight: 300,
            overflowY: "auto",
            zIndex: 50,
            boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
          }}
        >
          {loading && (
            <div style={{ padding: 12, color: "#94a3b8" }}>Recherche...</div>
          )}

          {!loading && results.length === 0 && (
            <div style={{ padding: 12, color: "#94a3b8" }}>Aucun résultat</div>
          )}

          {results.map((item) => (
            <div
              key={item.symbol}
              onClick={() => handleSelect(item.symbol)}
              style={{
                padding: "10px 16px",
                cursor: "pointer",
                borderBottom: "1px solid #f1f5f9",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
              onMouseEnter={(e) =>
                (e.currentTarget.style.background = "#f8fafc")
              }
              onMouseLeave={(e) => (e.currentTarget.style.background = "#fff")}
            >
              <div>
                <div style={{ fontWeight: 600 }}>{item.symbol}</div>
                <div style={{ fontSize: 13, color: "#64748b" }}>
                  {item.description}
                </div>
              </div>
              <div style={{ fontSize: 12, color: "#94a3b8" }}>{item.type}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
