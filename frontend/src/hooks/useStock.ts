import { useState, useEffect, useCallback } from "react";
import {
  searchStocks,
  getStock,
  getStockHistory,
  getIndicators,
  getScore,
  SearchResult,
  StockQuote,
  Candle,
  IndicatorsData,
  ScoreData,
} from "../services/api";

export function useStockSearch(query: string) {
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (query.length < 1) {
      setResults([]);
      return;
    }

    const timeout = setTimeout(async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await searchStocks(query);
        setResults(data);
      } catch {
        setError("Erreur lors de la recherche");
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 300);

    return () => clearTimeout(timeout);
  }, [query]);

  return { results, loading, error };
}

export function useStockDetail(ticker: string | undefined) {
  const [quote, setQuote] = useState<StockQuote | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!ticker) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getStock(ticker);
      setQuote(data);
    } catch {
      setError("Impossible de charger les données");
    } finally {
      setLoading(false);
    }
  }, [ticker]);

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, 60000);
    return () => clearInterval(interval);
  }, [refresh]);

  return { quote, loading, error, refresh };
}

export function useStockHistory(
  ticker: string | undefined,
  period: string = "1m"
) {
  const [candles, setCandles] = useState<Candle[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!ticker) return;

    let cancelled = false;
    setLoading(true);
    setError(null);

    getStockHistory(ticker, period)
      .then((data) => {
        if (!cancelled) setCandles(data.candles);
      })
      .catch(() => {
        if (!cancelled) setError("Impossible de charger l'historique");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [ticker, period]);

  return { candles, loading, error };
}

export function useIndicators(
  ticker: string | undefined,
  indicators: string = "rsi,macd,ma20,ma50,bb",
  period: string = "3m"
) {
  const [data, setData] = useState<IndicatorsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!ticker) return;

    let cancelled = false;
    setLoading(true);
    setError(null);

    getIndicators(ticker, indicators, period)
      .then((d) => {
        if (!cancelled) setData(d);
      })
      .catch(() => {
        if (!cancelled) setError("Impossible de charger les indicateurs");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [ticker, indicators, period]);

  return { data, loading, error };
}

export function useScore(ticker: string | undefined) {
  const [score, setScore] = useState<ScoreData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!ticker) return;

    let cancelled = false;
    setLoading(true);
    setError(null);

    getScore(ticker)
      .then((d) => {
        if (!cancelled) setScore(d);
      })
      .catch(() => {
        if (!cancelled) setError("Impossible de charger le score");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [ticker]);

  return { score, loading, error };
}
