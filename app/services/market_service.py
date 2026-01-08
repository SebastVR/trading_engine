import httpx
import pandas as pd
from app.util.timeframes import to_binance_interval

class MarketService:
    """
    Market data provider (Binance public REST).
    - Para BTCUSDT funciona sin API keys.
    - Más adelante puedes agregar FX/Oro con otro provider.
    """

    BINANCE_BASE = "https://api.binance.com"

    async def get_klines_df(self, symbol: str, timeframe: str, limit: int = 300) -> pd.DataFrame:
        interval = to_binance_interval(timeframe)
        url = f"{self.BINANCE_BASE}/api/v3/klines"
        params = {"symbol": symbol, "interval": interval, "limit": limit}

        # Temporal para desarrollo: verify=False
        # En producción usa verify=True con certificados correctos
        async with httpx.AsyncClient(timeout=20, verify=False) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            data = r.json()

        # Binance kline columns:
        # 0 open_time, 1 open, 2 high, 3 low, 4 close, 5 volume, 6 close_time, ...
        df = pd.DataFrame(data, columns=[
            "open_time","open","high","low","close","volume",
            "close_time","qav","num_trades","taker_base","taker_quote","ignore"
        ])

        df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
        df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")

        for col in ["open","high","low","close","volume"]:
            df[col] = df[col].astype(float)

        return df
