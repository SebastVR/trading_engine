def to_binance_interval(tf: str) -> str:
    tf = tf.strip().lower()
    mapping = {
        "1m": "1m",
        "3m": "3m",
        "5m": "5m",
        "15m": "15m",
        "30m": "30m",
        "1h": "1h",
        "2h": "2h",
        "4h": "4h",
        "6h": "6h",
        "12h": "12h",
        "1d": "1d",
        "1w": "1w",
    }
    if tf not in mapping:
        raise ValueError(f"Timeframe no soportado: {tf}. Usa: {list(mapping.keys())}")
    return mapping[tf]
