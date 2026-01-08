import numpy as np

def sma(values: np.ndarray, period: int) -> np.ndarray:
    out = np.full_like(values, np.nan, dtype=float)
    if period <= 0 or len(values) < period:
        return out
    cumsum = np.cumsum(values, dtype=float)
    out[period-1:] = (cumsum[period-1:] - np.concatenate(([0.0], cumsum[:-period])) ) / period
    return out

def rsi(close: np.ndarray, period: int = 14) -> np.ndarray:
    close = close.astype(float)
    delta = np.diff(close, prepend=close[0])
    gains = np.where(delta > 0, delta, 0.0)
    losses = np.where(delta < 0, -delta, 0.0)

    avg_gain = np.full_like(close, np.nan, dtype=float)
    avg_loss = np.full_like(close, np.nan, dtype=float)

    if len(close) <= period:
        return avg_gain

    avg_gain[period] = gains[1:period+1].mean()
    avg_loss[period] = losses[1:period+1].mean()

    for i in range(period+1, len(close)):
        avg_gain[i] = (avg_gain[i-1]*(period-1) + gains[i]) / period
        avg_loss[i] = (avg_loss[i-1]*(period-1) + losses[i]) / period

    rs = avg_gain / (avg_loss + 1e-12)
    rsi = 100 - (100 / (1 + rs))
    return rsi

def atr(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14) -> np.ndarray:
    high = high.astype(float)
    low = low.astype(float)
    close = close.astype(float)

    prev_close = np.roll(close, 1)
    prev_close[0] = close[0]

    tr = np.maximum(high - low, np.maximum(np.abs(high - prev_close), np.abs(low - prev_close)))
    out = np.full_like(close, np.nan, dtype=float)

    if len(close) <= period:
        return out

    out[period] = tr[1:period+1].mean()
    for i in range(period+1, len(close)):
        out[i] = (out[i-1]*(period-1) + tr[i]) / period
    return out
