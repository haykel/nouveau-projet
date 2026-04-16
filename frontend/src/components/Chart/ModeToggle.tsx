import { useState, useEffect } from "react";

interface Props {
  onChange: (advanced: boolean) => void;
}

const STORAGE_KEY = "chart-mode-advanced";

export default function ModeToggle({ onChange }: Props) {
  const [advanced, setAdvanced] = useState(() => {
    return localStorage.getItem(STORAGE_KEY) === "true";
  });

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, String(advanced));
    onChange(advanced);
  }, [advanced, onChange]);

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <span
        style={{
          fontSize: 13,
          color: advanced ? "#94a3b8" : "#0ea5e9",
          fontWeight: advanced ? 400 : 600,
        }}
      >
        Simple
      </span>
      <button
        onClick={() => setAdvanced(!advanced)}
        style={{
          width: 44,
          height: 24,
          borderRadius: 12,
          border: "none",
          background: advanced ? "#0ea5e9" : "#e2e8f0",
          cursor: "pointer",
          position: "relative",
          transition: "background 0.2s",
        }}
      >
        <div
          style={{
            width: 18,
            height: 18,
            borderRadius: 9,
            background: "#fff",
            position: "absolute",
            top: 3,
            left: advanced ? 23 : 3,
            transition: "left 0.2s",
            boxShadow: "0 1px 3px rgba(0,0,0,0.2)",
          }}
        />
      </button>
      <span
        style={{
          fontSize: 13,
          color: advanced ? "#0ea5e9" : "#94a3b8",
          fontWeight: advanced ? 600 : 400,
        }}
      >
        Avance
      </span>
    </div>
  );
}
