import math


class TechnicalIndicators:

    @staticmethod
    def calculate_ma(prices: list[float], period: int) -> list[float | None]:
        result = []
        for i in range(len(prices)):
            if i < period - 1:
                result.append(None)
            else:
                window = prices[i - period + 1 : i + 1]
                result.append(sum(window) / period)
        return result

    @staticmethod
    def calculate_ema(prices: list[float], period: int) -> list[float | None]:
        if len(prices) < period:
            return [None] * len(prices)

        result: list[float | None] = [None] * (period - 1)
        sma = sum(prices[:period]) / period
        result.append(sma)

        multiplier = 2 / (period + 1)
        prev = sma
        for i in range(period, len(prices)):
            ema = (prices[i] - prev) * multiplier + prev
            result.append(ema)
            prev = ema
        return result

    @staticmethod
    def calculate_rsi(prices: list[float], period: int = 14) -> list[float | None]:
        if len(prices) < period + 1:
            return [None] * len(prices)

        result: list[float | None] = [None] * period

        gains = []
        losses = []
        for i in range(1, period + 1):
            delta = prices[i] - prices[i - 1]
            gains.append(max(delta, 0))
            losses.append(max(-delta, 0))

        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period

        if avg_loss == 0:
            result.append(100.0)
        else:
            rs = avg_gain / avg_loss
            result.append(100 - 100 / (1 + rs))

        for i in range(period + 1, len(prices)):
            delta = prices[i] - prices[i - 1]
            gain = max(delta, 0)
            loss = max(-delta, 0)

            avg_gain = (avg_gain * (period - 1) + gain) / period
            avg_loss = (avg_loss * (period - 1) + loss) / period

            if avg_loss == 0:
                result.append(100.0)
            else:
                rs = avg_gain / avg_loss
                result.append(100 - 100 / (1 + rs))

        return result

    @staticmethod
    def calculate_macd(
        prices: list[float],
        fast: int = 12,
        slow: int = 26,
        signal_period: int = 9,
    ) -> dict[str, list[float | None]]:
        ema_fast = TechnicalIndicators.calculate_ema(prices, fast)
        ema_slow = TechnicalIndicators.calculate_ema(prices, slow)

        macd_line: list[float | None] = []
        for f, s in zip(ema_fast, ema_slow):
            if f is not None and s is not None:
                macd_line.append(f - s)
            else:
                macd_line.append(None)

        macd_values = [v for v in macd_line if v is not None]
        signal_raw = TechnicalIndicators.calculate_ema(macd_values, signal_period)

        signal_line: list[float | None] = []
        idx = 0
        for v in macd_line:
            if v is None:
                signal_line.append(None)
            else:
                signal_line.append(signal_raw[idx])
                idx += 1

        histogram: list[float | None] = []
        for m, s in zip(macd_line, signal_line):
            if m is not None and s is not None:
                histogram.append(m - s)
            else:
                histogram.append(None)

        return {"macd": macd_line, "signal": signal_line, "histogram": histogram}

    @staticmethod
    def calculate_bollinger_bands(
        prices: list[float], period: int = 20, num_std: float = 2.0
    ) -> dict[str, list[float | None]]:
        upper: list[float | None] = []
        middle: list[float | None] = []
        lower: list[float | None] = []

        for i in range(len(prices)):
            if i < period - 1:
                upper.append(None)
                middle.append(None)
                lower.append(None)
            else:
                window = prices[i - period + 1 : i + 1]
                mean = sum(window) / period
                variance = sum((x - mean) ** 2 for x in window) / period
                std = math.sqrt(variance)
                middle.append(mean)
                upper.append(mean + num_std * std)
                lower.append(mean - num_std * std)

        return {"upper": upper, "middle": middle, "lower": lower}

    @staticmethod
    def calculate_volume_profile(
        prices: list[float], volumes: list[int], bins: int = 20
    ) -> list[dict]:
        if not prices or not volumes:
            return []

        min_price = min(prices)
        max_price = max(prices)
        if min_price == max_price:
            return [{"price": min_price, "volume": sum(volumes)}]

        bin_size = (max_price - min_price) / bins
        profile: dict[int, int] = {}

        for price, vol in zip(prices, volumes):
            idx = min(int((price - min_price) / bin_size), bins - 1)
            profile[idx] = profile.get(idx, 0) + vol

        return [
            {
                "price": round(min_price + (i + 0.5) * bin_size, 2),
                "volume": profile.get(i, 0),
            }
            for i in range(bins)
        ]

    @staticmethod
    def calculate_score(
        prices: list[float], volumes: list[int]
    ) -> dict:
        if len(prices) < 30:
            return {
                "score": 50,
                "signal": "NEUTRE",
                "explanation": "Données insuffisantes pour une analyse fiable.",
            }

        rsi_values = TechnicalIndicators.calculate_rsi(prices)
        rsi = next((v for v in reversed(rsi_values) if v is not None), 50.0)

        # RSI score (30%)
        if rsi < 30:
            rsi_score = 90
        elif rsi < 40:
            rsi_score = 70
        elif rsi < 60:
            rsi_score = 50
        elif rsi < 70:
            rsi_score = 30
        else:
            rsi_score = 10

        # MA trend score (30%)
        ma20 = TechnicalIndicators.calculate_ma(prices, 20)
        latest_ma = next((v for v in reversed(ma20) if v is not None), None)
        current_price = prices[-1]

        if latest_ma is not None and latest_ma > 0:
            pct_above = (current_price - latest_ma) / latest_ma * 100
            if pct_above > 5:
                trend_score = 85
            elif pct_above > 0:
                trend_score = 65
            elif pct_above > -5:
                trend_score = 35
            else:
                trend_score = 15
        else:
            trend_score = 50

        # Volume score (20%)
        if len(volumes) >= 10:
            recent_avg = sum(volumes[-5:]) / 5
            older_avg = sum(volumes[-10:-5]) / 5
            if older_avg > 0:
                vol_ratio = recent_avg / older_avg
                if vol_ratio > 1.5:
                    vol_score = 80
                elif vol_ratio > 1.0:
                    vol_score = 60
                elif vol_ratio > 0.5:
                    vol_score = 40
                else:
                    vol_score = 20
            else:
                vol_score = 50
        else:
            vol_score = 50

        # Volatility score (20%)
        recent = prices[-20:] if len(prices) >= 20 else prices
        mean = sum(recent) / len(recent)
        if mean > 0:
            variance = sum((p - mean) ** 2 for p in recent) / len(recent)
            volatility = math.sqrt(variance) / mean * 100
            if volatility < 1:
                volatility_score = 70
            elif volatility < 3:
                volatility_score = 55
            elif volatility < 5:
                volatility_score = 40
            else:
                volatility_score = 25
        else:
            volatility_score = 50

        total = (
            rsi_score * 0.30
            + trend_score * 0.30
            + vol_score * 0.20
            + volatility_score * 0.20
        )
        score = round(total)

        if score >= 65:
            signal = "ACHAT"
            explanation = (
                f"Signaux positifs détectés. RSI à {rsi:.0f} (zone favorable), "
                f"prix au-dessus de la moyenne mobile. "
                f"Le volume et la volatilité soutiennent une tendance haussière."
            )
        elif score >= 40:
            signal = "NEUTRE"
            explanation = (
                f"Signaux mixtes. RSI à {rsi:.0f} (zone neutre). "
                f"Pas de tendance claire. "
                f"Il est conseillé d'attendre un signal plus fort avant d'agir."
            )
        else:
            signal = "VENTE"
            explanation = (
                f"Signaux négatifs détectés. RSI à {rsi:.0f} (zone de surachat), "
                f"prix sous la moyenne mobile. "
                f"La tendance baissière suggère la prudence."
            )

        return {
            "score": score,
            "signal": signal,
            "explanation": explanation,
            "details": {
                "rsi": round(rsi, 1),
                "rsi_score": rsi_score,
                "trend_score": trend_score,
                "volume_score": vol_score,
                "volatility_score": volatility_score,
            },
        }
